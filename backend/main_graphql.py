"""
Main application entry point with both REST and GraphQL support.
Optimized with cached component initialization and query complexity limits.
"""

import tornado.web
import tornado.ioloop
import logging
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# REST API handlers
from src.api.handlers import (
    MetadataHandler,
    GraphBuilderHandler,
    NodeExpandHandler,
    NodePayloadHandler,
    TreeBuilderHandler,
    TreeExpandHandler,
    TypeResolveHandler,
)

# GraphQL
from src.gql import create_schema, GraphQLHandler, GraphiQLHandler
from src.gql.complexity import QueryComplexityValidator

# Core services
from src.config.config_manager import ConfigurationManager
from src.data_providers.provider_registry import DataProviderRegistry
from src.services.graph_builder import GraphBuilder
from src.services.graph_service import GraphService
from src.services.tree_service import TreeService
from src.cache.cache_manager import CacheManager
from src.cache.memory_cache import MemoryCache


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Cached Components (Singletons)
# ============================================================================
# These are expensive to initialize and can be safely shared across requests
_cached_components = None


def _initialize_cached_components():
    """
    Initialize and cache expensive components that can be shared.
    This is called once at application startup.
    """
    global _cached_components
    
    if _cached_components is not None:
        return _cached_components
    
    logger.info("Initializing cached components (config, providers)...")
    
    # Initialize configuration manager (loads YAML, entity definitions)
    config_manager = ConfigurationManager()
    
    # Initialize provider registry (loads JSON data files)
    provider_registry = DataProviderRegistry()
    data_providers = provider_registry.get_all_providers()
    
    # Create graph builder (stateless, can be shared)
    graph_builder = GraphBuilder(config_manager, data_providers)
    
    _cached_components = {
        "config_manager": config_manager,
        "provider_registry": provider_registry,
        "data_providers": data_providers,
        "graph_builder": graph_builder,
    }
    
    logger.info("✓ Cached components initialized successfully")
    return _cached_components


def create_graphql_context():
    """
    Factory function to create GraphQL context for each request.
    
    Uses cached components (config, providers) and creates fresh
    service instances (cache manager, graph service, tree service)
    per request to ensure thread safety and proper cache isolation.
    """
    # Get cached components (shared across requests)
    cached = _initialize_cached_components()
    
    # Create fresh service instances per request
    # These maintain per-request state (cache, etc.)
    cache_manager = CacheManager(MemoryCache())
    graph_service = GraphService(cached["graph_builder"], cache_manager)
    tree_service = TreeService(cached["data_providers"], cached["config_manager"])
    
    return {
        # Cached components (shared, read-only)
        "config_manager": cached["config_manager"],
        "providers": cached["data_providers"],
        
        # Per-request service instances
        "graph_service": graph_service,
        "tree_service": tree_service,
        "cache_manager": cache_manager,
    }


def make_app(enable_graphql=True, enable_rest=True):
    """
    Create and configure the Tornado application.
    Initializes cached components once at startup.
    """
    # Initialize cached components at startup
    cached = _initialize_cached_components()
    
    # Create per-application service instances for REST endpoints
    # These will be shared across REST requests (Tornado handlers are singletons)
    cache_manager = CacheManager(MemoryCache())
    graph_service = GraphService(cached["graph_builder"], cache_manager)
    tree_service = TreeService(cached["data_providers"], cached["config_manager"])
    
    # Build routes
    routes = []

    # REST API routes
    if enable_rest:
        routes.extend(
            [
                (
                    r"/api/meta",
                    MetadataHandler,
                    dict(config_manager=cached["config_manager"]),
                ),
                (
                    r"/api/graph/build",
                    GraphBuilderHandler,
                    dict(graph_service=graph_service),
                ),
                (
                    r"/api/graph/node/expand",
                    NodeExpandHandler,
                    dict(graph_service=graph_service),
                ),
                (
                    r"/api/graph/node/payload",
                    NodePayloadHandler,
                    dict(data_providers=cached["data_providers"]),
                ),
                (
                    r"/api/tree/build",
                    TreeBuilderHandler,
                    dict(tree_service=tree_service),
                ),
                (
                    r"/api/tree/item/expand",
                    TreeExpandHandler,
                    dict(tree_service=tree_service),
                ),
                (
                    r"/api/type/resolve",
                    TypeResolveHandler,
                    dict(data_providers=cached["data_providers"]),
                ),
            ]
        )

    # GraphQL routes
    if enable_graphql:
        schema = create_schema()
        
        # Create complexity validator with custom limits
        complexity_validator = QueryComplexityValidator(
            max_complexity=1000,  # Maximum complexity score
            max_depth=10,         # Maximum nesting depth
        )
        
        routes.extend(
            [
                (
                    r"/graphql",
                    GraphQLHandler,
                    dict(
                        schema=schema,
                        context_factory=create_graphql_context,
                        complexity_validator=complexity_validator
                    ),
                ),
                (r"/graphiql", GraphiQLHandler),
            ]
        )

    return tornado.web.Application(routes, debug=True)


def main():
    """Main application entry point"""
    logger.info("=" * 70)
    logger.info("Starting Financial Data Relationship Explorer")
    logger.info("=" * 70)
    
    # Create application (this will initialize cached components)
    app = make_app(enable_graphql=True, enable_rest=True)
    port = 8888

    logger.info("")
    logger.info(f"Server running on port {port}")
    logger.info("")
    logger.info("REST API endpoints:")
    logger.info(f"  - GET  http://localhost:{port}/api/meta")
    logger.info(f"  - POST http://localhost:{port}/api/graph/build")
    logger.info(f"  - POST http://localhost:{port}/api/graph/node/expand")
    logger.info(f"  - GET  http://localhost:{port}/api/graph/node/payload")
    logger.info(f"  - POST http://localhost:{port}/api/tree/build")
    logger.info(f"  - POST http://localhost:{port}/api/tree/item/expand")
    logger.info(f"  - GET  http://localhost:{port}/api/type/resolve")
    logger.info("")
    logger.info("GraphQL endpoints:")
    logger.info(f"  - POST http://localhost:{port}/graphql")
    logger.info(f"  - GET  http://localhost:{port}/graphiql (Interactive explorer)")
    logger.info("")
    logger.info("Features:")
    logger.info("  ✓ Gzip compression for large responses")
    logger.info("  ✓ CORS enabled for all origins")
    logger.info("  ✓ GraphiQL interface for development")
    logger.info("  ✓ Caching enabled (5 min TTL)")
    logger.info("  ✓ Component caching for better performance")
    logger.info("  ✓ Query complexity limits (max: 1000, depth: 10)")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 70)

    app.listen(port)

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        tornado.ioloop.IOLoop.current().stop()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
