"""
Unit tests for entity types.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entities.entity_types import Stock, Option, Future, Bond, Listing, Exchange, InstrumentParty, Client, TreeListNode


class TestEntityTypes(unittest.TestCase):
    """Test cases for entity type classes"""
    
    def test_stock_creation(self):
        """Test Stock entity creation"""
        stock_data = {
            'instrumentId': 'TEST-001',
            'name': 'Test Stock',
            'instrument_type': 'Common Stock',
            'isin': 'US1234567890',
            'status': 'ACTIVE',
            'sector': 'Technology'
        }
        
        stock = Stock(stock_data)
        
        self.assertEqual(stock.id, 'TEST-001')
        self.assertEqual(stock.instrument_id, 'TEST-001')
        self.assertEqual(stock.name, 'Test Stock')
        self.assertEqual(stock.entity_type, 'Stock')
        
        node_dict = stock.to_node_dict()
        self.assertEqual(node_dict['id'], 'TEST-001')
        self.assertEqual(node_dict['titleLine1'], 'Common Stock')
        self.assertEqual(node_dict['titleLine2'], 'Test Stock')
        self.assertEqual(node_dict['refDataType'], 'Stock')
    
    def test_option_creation(self):
        """Test Option entity creation"""
        option_data = {
            'instrumentId': 'OPT-001',
            'name': 'Test Option',
            'instrument_type': 'Call Option',
            'underlyingInstrumentId': 'TEST-001',
            'optionType': 'Call',
            'strike': '100.00',
            'expirationDate': '2024-12-20',
            'status': 'ACTIVE'
        }
        
        option = Option(option_data)
        
        self.assertEqual(option.id, 'OPT-001')
        self.assertEqual(option.underlying_instrument_id, 'TEST-001')
        self.assertEqual(option.entity_type, 'Option')
        
        node_dict = option.to_node_dict()
        self.assertEqual(node_dict['refDataType'], 'Option')
        self.assertEqual(node_dict['additionalLines']['Option Type'], 'Call')
    
    def test_tree_list_node_creation(self):
        """Test TreeListNode creation"""
        tree_data = {
            'id': 'TREE-001',
            'titleLine1': 'Click to view Options',
            'titleLine2': '',
            'totalCount': 150,
            'sourceEntityId': 'STOCK-001',
            'relationshipName': 'IS_UNDERLYING_FOR',
            'targetType': 'Option'
        }
        
        tree_node = TreeListNode(tree_data)
        
        self.assertEqual(tree_node.id, 'TREE-001')
        self.assertEqual(tree_node.source_entity_id, 'STOCK-001')
        self.assertEqual(tree_node.relationship_name, 'IS_UNDERLYING_FOR')
        self.assertEqual(tree_node.target_type, 'Option')
        
        node_dict = tree_node.to_node_dict()
        self.assertEqual(node_dict['displayType'], 'tree-list')
        self.assertEqual(node_dict['additionalLines']['Total Count'], '150')


if __name__ == '__main__':
    unittest.main()
