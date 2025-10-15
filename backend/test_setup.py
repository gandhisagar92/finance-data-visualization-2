"""
Simple test to verify the application setup.
Run this to test basic functionality before starting the server.
"""

import sys
import os

# Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config.config_manager import ConfigurationManager
from data_providers.provider_registry import DataProviderRegistry
from services.graph_builder import GraphBuilder


def test_configuration():
    """Test configuration manager"""
    print("Testing Configuration Manager...")
    config_manager = ConfigurationManager()

    # Test metadata
    metadata = config_manager.get_metadata_for_api()
    assert "referenceDataTypes" in metadata
    print(f"✓ Loaded {len(metadata['referenceDataTypes'])} reference data types")

    # Test entity definitions
    stock_def = config_manager.get_entity_definition("Stock")
    assert stock_def is not None
    print(f"✓ Stock entity definition loaded")

    # Test relationships
    stock_rels = config_manager.get_entity_relationships("Stock")
    assert len(stock_rels) > 0
    print(f"✓ Stock has {len(stock_rels)} relationships")

    print("Configuration Manager: PASSED\n")


def test_data_providers():
    """Test data provider registry"""
    print("Testing Data Providers...")
    registry = DataProviderRegistry()

    # Test stock provider
    stock_provider = registry.get_provider("Stock")
    assert stock_provider is not None
    print("✓ Stock provider initialized")

    # Test fetching a stock
    stock = stock_provider.get_entity_by_id(
        "Stock", "instrumentId", {"instrumentId": "STK-100"}
    )
    assert stock is not None
    assert stock.data.get("instrumentId") == "STK-100"
    print(f"✓ Fetched stock: {stock.data.get('titleLine2')}")

    # Test listing provider
    listing_provider = registry.get_provider("Listing")
    assert listing_provider is not None
    print("✓ Listing provider initialized")

    # Test exchange provider
    exchange_provider = registry.get_provider("Exchange")
    assert exchange_provider is not None
    print("✓ Exchange provider initialized")

    print("Data Providers: PASSED\n")


def test_graph_builder():
    """Test graph builder"""
    print("Testing Graph Builder...")
    config_manager = ConfigurationManager()
    registry = DataProviderRegistry()

    graph_builder = GraphBuilder(config_manager, registry.get_all_providers())

    # Build a simple graph
    result = graph_builder.build_graph(
        "Stock", "instrumentId", {"instrumentId": "STK-100"}
    )

    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) > 0

    print(
        f"✓ Built graph with {len(result['nodes'])} nodes and {len(result['edges'])} edges"
    )

    # Print first few nodes
    for i, node in enumerate(result["nodes"][:3]):
        print(
            f"  Node {i+1}: {node.get('titleLine1', '')} - {node.get('titleLine2', '')}"
        )

    print("Graph Builder: PASSED\n")


def test_entity_transformation():
    """Test entity to node transformation"""
    print("Testing Entity Transformation...")
    config_manager = ConfigurationManager()
    registry = DataProviderRegistry()

    stock_provider = registry.get_provider("Stock")
    stock = stock_provider.get_entity_by_id(
        "Stock", "instrumentId", {"instrumentId": "STK-100"}
    )

    # Get entity definition and transform
    entity_def = config_manager.get_entity_definition("Stock")
    node_dict = stock.to_graph_node_dict(entity_def)

    assert "id" in node_dict
    assert "titleLine1" in node_dict
    assert "refDataType" in node_dict
    assert node_dict["refDataType"] == "Stock"

    print(f"✓ Transformed entity to node:")
    print(f"  ID: {node_dict.get('id')}")
    print(f"  Title: {node_dict.get('titleLine1')} - {node_dict.get('titleLine2')}")
    print(f"  Status: {node_dict.get('status')}")

    print("Entity Transformation: PASSED\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Financial Data Explorer - Component Tests")
    print("=" * 60 + "\n")

    try:
        test_configuration()
        test_data_providers()
        test_graph_builder()
        test_entity_transformation()

        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now start the server with: python main.py")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
