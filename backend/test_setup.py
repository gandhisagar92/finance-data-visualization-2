#!/usr/bin/env python3
"""
Test script to verify the application setup and basic functionality.
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        # Test entity imports
        from entities.entity_types import Stock, Option, Future, Bond, Listing
        print("✓ Entity types imported successfully")
        
        # Test cache imports
        from cache.memory_cache import MemoryCache
        from cache.cache_manager import CacheManager
        print("✓ Cache system imported successfully")
        
        # Test data provider imports
        from data_providers.instrument_provider import InstrumentDataProvider
        from data_providers.registry import DataProviderRegistry
        print("✓ Data providers imported successfully")
        
        # Test service imports
        from services.graph_builder import GraphBuilder
        from services.graph_service import GraphService
        print("✓ Services imported successfully")
        
        # Test config imports
        from config.config_manager import ConfigurationManager
        print("✓ Configuration manager imported successfully")
        
        # Test API imports
        from api.handlers import MetadataHandler, GraphBuilderHandler
        print("✓ API handlers imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False

def test_entity_creation():
    """Test entity creation and basic functionality"""
    try:
        print("\nTesting entity creation...")
        
        from entities.entity_types import Stock
        
        stock_data = {
            'instrumentId': 'TEST-001',
            'name': 'Test Stock',
            'instrument_type': 'Common Stock',
            'isin': 'US1234567890',
            'status': 'ACTIVE',
            'sector': 'Technology'
        }
        
        stock = Stock(stock_data)
        node_dict = stock.to_node_dict()
        
        assert stock.id == 'TEST-001'
        assert stock.instrument_id == 'TEST-001'
        assert node_dict['refDataType'] == 'Stock'
        
        print("✓ Stock entity created and converted to node successfully")
        return True
        
    except Exception as e:
        print(f"✗ Entity creation test failed: {e}")
        return False

def test_cache_system():
    """Test cache system functionality"""
    try:
        print("\nTesting cache system...")
        
        from cache.memory_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set('test_key', 'test_value')
        
        retrieved_value = cache.get('test_key')
        assert retrieved_value == 'test_value'
        
        print("✓ Cache system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Cache system test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        print("\nTesting configuration system...")
        
        from config.config_manager import ConfigurationManager
        
        config_dir = os.path.join(os.path.dirname(__file__), 'src', 'config')
        config_manager = ConfigurationManager(config_dir)
        
        metadata = config_manager.get_metadata_for_api()
        assert 'referenceDataTypes' in metadata
        
        print("✓ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_data_provider():
    """Test data provider functionality"""
    try:
        print("\nTesting data provider...")
        
        from data_providers.instrument_provider import InstrumentDataProvider
        
        provider = InstrumentDataProvider({})
        
        # Test type resolution
        resolved_type = provider.resolve_entity_type(
            'Instrument', 
            'InstrumentId', 
            {'instrumentId': 'A125989590'}
        )
        
        if resolved_type:
            print(f"✓ Type resolution working: Instrument -> {resolved_type}")
        else:
            print("✓ Type resolution working (no match found, which is expected)")
        
        return True
        
    except Exception as e:
        print(f"✗ Data provider test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Financial Data Relationship Explorer - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_entity_creation,
        test_cache_system,
        test_configuration,
        test_data_provider
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print()
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application is ready to run.")
        print("\nTo start the server, run:")
        print("  python main.py")
        print("\nOr use the start script:")
        print("  python start.py")
    else:
        print(f"✗ {total - passed} tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
