"""
Test GraphQL setup and basic functionality.
"""

import sys
import os

# Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.graphql import create_schema
from src.config.config_manager import ConfigurationManager
from src.data_providers.provider_registry import DataProviderRegistry
from src.services.graph_builder import GraphBuilder
from src.services.graph_service import GraphService
from src.cache.cache_manager import CacheManager
from src.cache.memory_cache import MemoryCache


def test_schema_creation():
    """Test GraphQL schema creation"""
    print("Testing GraphQL Schema Creation...")
    try:
        schema = create_schema()
        assert schema is not None
        print("✓ GraphQL schema created successfully")

        # Print schema
        schema_str = str(schema)
        print(f"✓ Schema has {schema_str.count('type ')} types")
        print("GraphQL Schema Creation: PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_graphql_query():
    """Test executing a GraphQL query"""
    print("Testing GraphQL Query Execution...")
    try:
        # Create schema
        schema = create_schema()

        # Create context
        config_manager = ConfigurationManager()
        provider_registry = DataProviderRegistry()
        data_providers = provider_registry.get_all_providers()
        graph_builder = GraphBuilder(config_manager, data_providers)
        cache_manager = CacheManager(MemoryCache())
        graph_service = GraphService(graph_builder, cache_manager)

        context = {
            "config_manager": config_manager,
            "providers": data_providers,
            "graph_service": graph_service,
        }

        # Test query
        query = """
        query TestQuery {
            getMetadata {
                referenceDataTypes {
                    refDataType
                    idTypes {
                        type
                        inputs {
                            id
                            label
                            kind
                            required
                        }
                    }
                }
            }
        }
        """

        # Execute query (sync version for testing)
        import asyncio

        result = asyncio.run(schema.execute(query, context_value=context))

        if result.errors:
            print(f"❌ Query execution had errors: {result.errors}")
            return False

        if result.data:
            metadata = result.data.get("getMetadata", {})
            ref_types = metadata.get("referenceDataTypes", [])
            print(f"✓ Query executed successfully")
            print(f"✓ Retrieved {len(ref_types)} reference data types")
            print("GraphQL Query Execution: PASSED\n")
            return True
        else:
            print("❌ No data returned from query")
            return False

    except Exception as e:
        print(f"❌ Query execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_build_graph_query():
    """Test build graph GraphQL query"""
    print("Testing Build Graph Query...")
    try:
        # Create schema
        schema = create_schema()

        # Create context
        config_manager = ConfigurationManager()
        provider_registry = DataProviderRegistry()
        data_providers = provider_registry.get_all_providers()
        graph_builder = GraphBuilder(config_manager, data_providers)
        cache_manager = CacheManager(MemoryCache())
        graph_service = GraphService(graph_builder, cache_manager)

        from src.services.tree_service import TreeService

        tree_service = TreeService(data_providers, config_manager)

        context = {
            "config_manager": config_manager,
            "providers": data_providers,
            "graph_service": graph_service,
            "tree_service": tree_service,
        }

        # Test build graph query
        query = """
        query BuildStockGraph {
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
                    maxDepth
                }
            }
        }
        """

        # Execute query
        import asyncio

        result = asyncio.run(schema.execute(query, context_value=context))

        if result.errors:
            print(f"❌ Build graph query had errors:")
            for error in result.errors:
                print(f"  - {error}")
            import traceback

            traceback.print_exc()
            return False

        if result.data:
            graph_data = result.data.get("buildGraph", {})
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            metadata = graph_data.get("metadata", {})

            print(f"✓ Build graph query executed successfully")
            print(f"✓ Graph has {len(nodes)} nodes and {len(edges)} edges")
            print(f"✓ Max depth: {metadata.get('maxDepth', 0)}")

            if nodes:
                first_node = nodes[0]
                print(
                    f"✓ First node: {first_node.get('titleLine1')} - {first_node.get('titleLine2')}"
                )

            print("Build Graph Query: PASSED\n")
            return True
        else:
            print("❌ No data returned from build graph query")
            return False

    except Exception as e:
        print(f"❌ Build graph query failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("GraphQL Setup Tests")
    print("=" * 70 + "\n")

    tests = [
        test_schema_creation,
        test_graphql_query,
        test_build_graph_query,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n✅ All tests passed! GraphQL is ready to use.")
        print("\nYou can now start the server with:")
        print("  python main_graphql.py")
        print("\nThen visit:")
        print("  http://localhost:8888/graphiql")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
