#!/usr/bin/env python3
"""
Build graph using GraphQL query
"""

import urllib.request
import urllib.parse
import json


def build_graph():
    """Build graph from GraphQL endpoint"""

    url = "http://localhost:8888/graphql"

    # GraphQL query for building graph
    query = """
    query BuildGraph($input: BuildGraphInput!) {
      buildGraph(input: $input) {
        nodes {
          id
          titleLine1
          titleLine2
          status
          refDataType
          idType
          idValue {
            key
            value
          }
          expandable
          displayType
          additionalLines {
            key
            value
          }
          asOf
          source
          payload
        }
        edges {
          source
          target
          relationship
          metadata {
            key
            value
          }
        }
        metadata {
          nodeCount
          edgeCount
          maxDepth
          executionTimeMs
        }
      }
    }
    """

    # Variables for the query (converted from your REST format)
    variables = {
        "input": {
            "refDataType": "Stock",
            "idType": "instrumentId",
            "idValue": [{"key": "instrumentId", "value": "STK-100"}],
            "source": "Athena",
            "effectiveDatetime": "2024-01-15T00:00:00",
            "maxDepth": 2,
        }
    }

    # Create the request payload
    payload = {"query": query, "variables": variables}

    try:
        # Convert to JSON and encode
        data = json.dumps(payload).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode("utf-8")
            result = json.loads(response_data)

            print("GraphQL Build Graph Query Result:")
            print("=" * 50)
            print(json.dumps(result, indent=2))

            # Pretty print the graph result
            if "data" in result and result["data"] and "buildGraph" in result["data"]:
                graph = result["data"]["buildGraph"]

                print(f"\n\nGraph Summary:")
                print("-" * 50)

                if "metadata" in graph and graph["metadata"]:
                    metadata = graph["metadata"]
                    print(f"📊 Nodes: {metadata.get('nodeCount', 0)}")
                    print(f"🔗 Edges: {metadata.get('edgeCount', 0)}")
                    print(f"🔍 Max Depth: {metadata.get('maxDepth', 0)}")
                    print(
                        f"⏱️ Execution Time: {metadata.get('executionTimeMs', 0):.2f} ms"
                    )

                nodes = graph.get("nodes", [])
                edges = graph.get("edges", [])

                print(f"\n📋 Nodes ({len(nodes)}):")
                for i, node in enumerate(nodes):
                    print(
                        f"  {i+1}. {node.get('titleLine1', 'Unknown')} ({node.get('refDataType', 'Unknown')})"
                    )
                    if node.get("titleLine2"):
                        print(f"      {node.get('titleLine2')}")
                    print(
                        f"      ID: {node.get('id', 'N/A')} | Status: {node.get('status', 'N/A')}"
                    )

                print(f"\n🔗 Relationships ({len(edges)}):")
                for i, edge in enumerate(edges):
                    print(
                        f"  {i+1}. {edge.get('source', 'Unknown')} --[{edge.get('relationship', 'Unknown')}]--> {edge.get('target', 'Unknown')}"
                    )

            else:
                print("\n❌ No graph data returned or error occurred")
                if "errors" in result:
                    print("Errors:")
                    for error in result["errors"]:
                        print(f"  - {error.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"Error building graph: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    build_graph()
