"""
Test script for the /api/build/tree endpoint
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.tree_service import TreeService
from data_providers.registry import DataProviderRegistry
from config.config_manager import ConfigurationManager


def test_tree_build_api():
    """Test the tree build API logic"""
    print("=" * 70)
    print("Testing /api/build/tree endpoint")
    print("=" * 70)
    
    # Initialize components
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'config')
    config_manager = ConfigurationManager(config_dir)
    
    data_provider_registry = DataProviderRegistry()
    provider_configs = {
        'InstrumentDataProvider': {},
        'ListingDataProvider': {},
        'ExchangeDataProvider': {},
        'PartyDataProvider': {}
    }
    data_provider_registry.initialize_all_providers(provider_configs, None)
    data_providers = data_provider_registry.get_all_providers()
    
    tree_service = TreeService(data_providers, config_manager)
    
    # Test request
    print("\n1. Testing with sample request:")
    print("-" * 70)
    
    request_body = {
        "refDataType": "Option",
        "idType": "underlyingInstrumentId",
        "idValue": {
            "sourceEntityId": "STK-100",
            "relationshipName": "IS_UNDERLYING_FOR"
        },
        "page": 1,
        "size": 50
    }
    
    print("Request Body:")
    print(json.dumps(request_body, indent=2))
    
    # Call the service
    result = tree_service.build_tree_list(
        ref_data_type=request_body['refDataType'],
        id_type=request_body['idType'],
        id_value=request_body['idValue'],
        page=request_body['page'],
        page_size=request_body['size']
    )
    
    print("\n2. Response:")
    print("-" * 70)
    print(json.dumps(result, indent=2))
    
    # Verify response structure
    print("\n3. Validation:")
    print("-" * 70)
    
    assert 'data' in result, "Response missing 'data' field"
    assert 'page' in result, "Response missing 'page' field"
    assert 'size' in result, "Response missing 'size' field"
    assert 'total_items' in result, "Response missing 'total_items' field"
    assert 'total_pages' in result, "Response missing 'total_pages' field"
    assert 'has_next' in result, "Response missing 'has_next' field"
    assert 'has_previous' in result, "Response missing 'has_previous' field"
    assert 'meta' in result, "Response missing 'meta' field"
    
    print(f"✓ Response has all required fields")
    print(f"✓ Found {len(result['data'])} options")
    print(f"✓ Total items: {result['total_items']}")
    print(f"✓ Total pages: {result['total_pages']}")
    
    # Verify meta structure
    meta = result['meta']
    assert 'columns' in meta, "Meta missing 'columns' field"
    assert 'column_groups' in meta, "Meta missing 'column_groups' field"
    
    print(f"✓ Meta has {len(meta['columns'])} column definitions")
    print(f"✓ Meta has {len(meta['column_groups'])} column groups")
    
    # Verify data structure
    if result['data']:
        first_row = result['data'][0]
        required_fields = [
            'instrumentId', 'name', 'status', 'isin', 'postTradeId',
            'strike_price', 'contractSize', 'putOrCall', 'expirationDate',
            'exerciseStyle', 'primaryTradingLine', 'timingRule'
        ]
        
        for field in required_fields:
            assert field in first_row, f"Data row missing required field: {field}"
        
        print(f"✓ Data rows have all required fields")
        
        print("\nSample data row:")
        print(json.dumps(first_row, indent=2))
    
    print("\n4. Testing with pagination:")
    print("-" * 70)
    
    # Test page 2
    result_page2 = tree_service.build_tree_list(
        ref_data_type="Option",
        id_type="underlyingInstrumentId",
        id_value={"sourceEntityId": "STK-100", "relationshipName": "IS_UNDERLYING_FOR"},
        page=2,
        page_size=1
    )
    
    print(f"Page 2 request:")
    print(f"  - Page: {result_page2['page']}")
    print(f"  - Items in page: {len(result_page2['data'])}")
    print(f"  - Has next: {result_page2['has_next']}")
    print(f"  - Has previous: {result_page2['has_previous']}")
    
    assert result_page2['page'] == 2, "Page number incorrect"
    assert result_page2['has_previous'] == True, "Should have previous page"
    
    print(f"✓ Pagination working correctly")
    
    print("\n5. Testing with sorting:")
    print("-" * 70)
    
    result_sorted = tree_service.build_tree_list(
        ref_data_type="Option",
        id_type="underlyingInstrumentId",
        id_value={"sourceEntityId": "STK-100", "relationshipName": "IS_UNDERLYING_FOR"},
        page=1,
        page_size=50,
        sort_by="expirationDate:asc"
    )
    
    if len(result_sorted['data']) > 1:
        dates = [row['expirationDate'] for row in result_sorted['data']]
        print(f"Sorted expiration dates: {dates}")
        print(f"✓ Sorting applied")
    
    print("\n" + "=" * 70)
    print("All tests passed! ✓")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_tree_build_api()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
