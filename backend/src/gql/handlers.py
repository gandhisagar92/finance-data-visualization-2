"""
Tornado GraphQL handler with Gzip compression support and query complexity limits.
"""

import tornado.web
import json
import gzip
from typing import Dict, Any, Optional
import logging
from graphql import parse, GraphQLError

from graphene import Schema
from src.gql.complexity import QueryComplexityValidator


logger = logging.getLogger(__name__)


class GraphQLHandler(tornado.web.RequestHandler):
    """
    Tornado handler for GraphQL requests with Gzip compression and complexity limits.
    Supports both query and mutation operations.
    """

    def initialize(
        self, 
        schema, 
        context_factory,
        complexity_validator: Optional[QueryComplexityValidator] = None
    ):
        """
        Initialize the handler with GraphQL schema and context factory.

        Args:
            schema: Graphene GraphQL schema
            context_factory: Function that creates context for each request
            complexity_validator: Optional query complexity validator
        """
        self.schema = schema
        self.context_factory = context_factory
        self.complexity_validator = complexity_validator or QueryComplexityValidator(
            max_complexity=1000,
            max_depth=10
        )

    def set_default_headers(self):
        """Set CORS headers"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Accept-Encoding, Authorization",
        )
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def options(self):
        """Handle OPTIONS requests for CORS"""
        self.set_status(204)
        self.finish()

    async def get(self):
        """
        Handle GET requests for GraphQL.
        Supports GraphQL query via query parameter.
        """
        query = self.get_argument("query", None)
        variables = self.get_argument("variables", None)
        operation_name = self.get_argument("operationName", None)

        if not query:
            self.set_status(400)
            self.write_error_response("BAD_REQUEST", "No query provided")
            return

        # Parse variables if provided
        if variables:
            try:
                variables = json.loads(variables)
            except json.JSONDecodeError:
                self.set_status(400)
                self.write_error_response("BAD_REQUEST", "Invalid variables JSON")
                return

        await self._execute_graphql(query, variables, operation_name)

    async def post(self):
        """
        Handle POST requests for GraphQL.
        Supports both application/json and application/graphql.
        """
        content_type = self.request.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                body = json.loads(self.request.body)
                query = body.get("query")
                variables = body.get("variables")
                operation_name = body.get("operationName")
            except json.JSONDecodeError as e:
                self.set_status(400)
                self.write_error_response("BAD_REQUEST", f"Invalid JSON: {str(e)}")
                return
        elif "application/graphql" in content_type:
            query = self.request.body.decode("utf-8")
            variables = None
            operation_name = None
        else:
            self.set_status(400)
            self.write_error_response(
                "BAD_REQUEST", f"Unsupported content type: {content_type}"
            )
            return

        if not query:
            self.set_status(400)
            self.write_error_response("BAD_REQUEST", "No query provided")
            return

        await self._execute_graphql(query, variables, operation_name)

    async def _execute_graphql(
        self,
        query: str,
        variables: Optional[Dict[str, Any]],
        operation_name: Optional[str],
    ):
        """
        Execute a GraphQL query and return the response.
        Applies complexity validation and Gzip compression.
        """
        try:
            # Parse the query
            try:
                document_ast = parse(query)
            except GraphQLError as e:
                self.set_status(400)
                self.write_error_response(
                    "GRAPHQL_PARSE_ERROR",
                    f"Query parsing failed: {str(e)}"
                )
                return
            
            # Validate query complexity
            try:
                self.complexity_validator.validate_query(document_ast)
            except GraphQLError as e:
                self.set_status(400)
                self.write_error_response(
                    "QUERY_TOO_COMPLEX",
                    str(e)
                )
                return
            
            # Create context for this request
            context = self.context_factory()

            # Execute the GraphQL query using Graphene
            result = self.schema.execute(
                query,
                variables=variables,
                operation_name=operation_name,
                context=context,
            )

            # Build response
            response_data = {"data": result.data}

            if result.errors:
                response_data["errors"] = [
                    self._format_graphql_error(error) for error in result.errors
                ]
                logger.error(f"GraphQL errors: {result.errors}")

            # Convert to JSON
            response_json = json.dumps(
                response_data, default=str, separators=(",", ":")
            )

            # Check if client accepts gzip
            accept_encoding = self.request.headers.get("Accept-Encoding", "")
            use_gzip = "gzip" in accept_encoding.lower()

            # Write response with optional compression
            self._write_response(response_json, use_gzip)

        except Exception as e:
            logger.exception(f"Error executing GraphQL query: {e}")
            self.set_status(500)
            self.write_error_response(
                "INTERNAL_ERROR", f"Internal server error: {str(e)}"
            )

    def _write_response(self, response_json: str, use_gzip: bool):
        """
        Write the response with optional Gzip compression.

        Args:
            response_json: JSON response string
            use_gzip: Whether to apply Gzip compression
        """
        self.set_header("Content-Type", "application/json; charset=utf-8")

        if use_gzip:
            # Compress the response
            compressed_data = gzip.compress(response_json.encode("utf-8"))

            # Set compression headers
            self.set_header("Content-Encoding", "gzip")
            self.set_header("Content-Length", str(len(compressed_data)))

            # Log compression ratio
            original_size = len(response_json.encode("utf-8"))
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            logger.info(
                f"Response compressed: {original_size} -> {compressed_size} bytes "
                f"({compression_ratio:.1f}% reduction)"
            )

            self.write(compressed_data)
        else:
            # Write uncompressed response
            self.write(response_json)

        self.finish()

    def _format_graphql_error(self, error) -> Dict[str, Any]:
        """Format a GraphQL error for the response"""
        formatted = {
            "message": str(error.message) if hasattr(error, "message") else str(error)
        }

        if hasattr(error, "locations") and error.locations:
            formatted["locations"] = [
                {"line": loc.line, "column": loc.column} for loc in error.locations
            ]

        if hasattr(error, "path") and error.path:
            formatted["path"] = error.path

        if hasattr(error, "extensions") and error.extensions:
            formatted["extensions"] = error.extensions
        
        # Add custom error codes if available
        if hasattr(error, "original_error") and error.original_error:
            original = error.original_error
            if hasattr(original, "error_code"):
                if "extensions" not in formatted:
                    formatted["extensions"] = {}
                formatted["extensions"]["code"] = original.error_code

        return formatted

    def write_error_response(self, error_code: str, message: str):
        """Write a standardized error response"""
        error_response = {
            "errors": [{"message": message, "extensions": {"code": error_code}}]
        }

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(error_response))
        self.finish()


class GraphiQLHandler(tornado.web.RequestHandler):
    """
    Handler for GraphiQL interface (development only).
    Provides an interactive GraphQL explorer.
    """

    def get(self):
        """Serve the GraphiQL interface"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GraphiQL - Financial Data Explorer</title>
            <style>
                body {
                    height: 100vh;
                    margin: 0;
                    overflow: hidden;
                }
                #graphiql {
                    height: 100vh;
                }
            </style>
            <link href="https://unpkg.com/graphiql/graphiql.min.css" rel="stylesheet" />
        </head>
        <body>
            <div id="graphiql">Loading...</div>
            <script
                crossorigin
                src="https://unpkg.com/react/umd/react.production.min.js"
            ></script>
            <script
                crossorigin
                src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"
            ></script>
            <script
                crossorigin
                src="https://unpkg.com/graphiql/graphiql.min.js"
            ></script>
            <script>
                const fetcher = GraphiQL.createFetcher({
                    url: '/graphql',
                });
                
                ReactDOM.render(
                    React.createElement(GraphiQL, { 
                        fetcher: fetcher,
                        defaultQuery: `# Welcome to GraphiQL - Financial Data Relationship Explorer
# 
# This is an interactive GraphQL explorer with:
# ✓ Query complexity limits (max 1000, depth 10)
# ✓ Gzip compression for large responses
# ✓ Real-time query validation
#
# Type queries in the left panel and press Ctrl-Enter to execute.
#
# Example query:

query GetStockGraph {
  buildGraph(input: {
    refDataType: "Stock"
    idType: "instrumentId"
    idValue: [{key: "instrumentId", value: "STK-100"}]
    maxDepth: 2
  }) {
    nodes {
      id
      titleLine1
      titleLine2
      status
      additionalLines {
        key
        value
      }
      refDataType
      expandable
    }
    edges {
      source
      target
      relationship
    }
    metadata {
      nodeCount
      edgeCount
      executionTimeMs
    }
  }
}

# Try this query to see metadata:
# query GetMetadata {
#   getMetadata {
#     referenceDataTypes {
#       refDataType
#       idTypes {
#         type
#       }
#     }
#   }
# }
`
                    }),
                    document.getElementById('graphiql'),
                );
            </script>
        </body>
        </html>
        """
        self.set_header("Content-Type", "text/html")
        self.write(html)
