"""
Unit tests for cache system.
"""

import unittest
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cache.memory_cache import MemoryCache
from cache.cache_manager import CacheManager


class TestCacheSystem(unittest.TestCase):
    """Test cases for cache system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = MemoryCache()
        self.cache_manager = CacheManager(self.cache)
    
    def test_basic_cache_operations(self):
        """Test basic cache get/set/delete operations"""
        # Test set and get
        self.cache.set('test_key', 'test_value')
        self.assertEqual(self.cache.get('test_key'), 'test_value')
        
        # Test exists
        self.assertTrue(self.cache.exists('test_key'))
        self.assertFalse(self.cache.exists('nonexistent_key'))
        
        # Test delete
        self.cache.delete('test_key')
        self.assertIsNone(self.cache.get('test_key'))
    
    def test_cache_ttl(self):
        """Test cache TTL functionality"""
        # Set with 1 second TTL
        self.cache.set('ttl_key', 'ttl_value', ttl=1)
        self.assertEqual(self.cache.get('ttl_key'), 'ttl_value')
        
        # Wait for expiration and test
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('ttl_key'))
    
    def test_cache_manager_key_generation(self):
        """Test cache manager key generation"""
        key1 = self.cache_manager.generate_key('prefix', 'arg1', 'arg2', param1='value1')
        key2 = self.cache_manager.generate_key('prefix', 'arg1', 'arg2', param1='value1')
        key3 = self.cache_manager.generate_key('prefix', 'arg1', 'arg2', param1='value2')
        
        # Same arguments should generate same key
        self.assertEqual(key1, key2)
        
        # Different arguments should generate different keys
        self.assertNotEqual(key1, key3)
    
    def test_cache_manager_enable_disable(self):
        """Test cache manager enable/disable functionality"""
        # Test with cache enabled
        self.cache_manager.set('enable_test', 'enabled_value')
        self.assertEqual(self.cache_manager.get('enable_test'), 'enabled_value')
        
        # Disable cache
        self.cache_manager.disable()
        self.cache_manager.set('disable_test', 'disabled_value')
        self.assertIsNone(self.cache_manager.get('disable_test'))
        
        # Re-enable cache
        self.cache_manager.enable()
        self.cache_manager.set('reenable_test', 'reenabled_value')
        self.assertEqual(self.cache_manager.get('reenable_test'), 'reenabled_value')
    
    def test_cached_method_decorator(self):
        """Test cached method decorator"""
        call_count = 0
        
        @self.cache_manager.cached_method(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Second call with same arguments should use cache
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Call with different arguments should execute function
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)


if __name__ == '__main__':
    unittest.main()
