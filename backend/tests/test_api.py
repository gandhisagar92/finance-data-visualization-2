"""
Integration tests for the API endpoints.
"""

import unittest
import json
import sys
import os
import tornado.testing

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import create_application


class TestAPIEndpoints(tornado.testing.AsyncHTTPTestCase):
    """Integration tests for API endpoints"""
    
    def get_app(self):
        """Get the application for testing"""
        return create_application()
    
    def test_metadata_endpoint(self):
        """Test metadata endpoint"""
        response = self.fetch('/api/meta')
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertIn('referenceDataTypes', data)
        self.assertIsInstance(data['referenceDataTypes'], list)
        
        # Check that Instrument type exists
        instrument_type = None
        for ref_type in data['referenceDataTypes']:
            if ref_type['refDataType'] == 'Instrument':
                instrument_type = ref_type
                break
        
        self.assertIsNotNone(instrument_type)
        self.assertIn('idTypes', instrument_type)
    
    def test_graph_build_endpoint(self):
        """Test graph build endpoint"""
        request_data = {
            "refDataType": "Instrument",
            "idType": "InstrumentId",
            "idValue": {"instrumentId": "A125989590"},
            "source": "Athena",
            "effectiveDatetime": "2024-01-15 00:00:00"
        }
        
        response = self.fetch(
            '/api/graph/build',
            method='POST',
            body=json.dumps(request_data),
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['edges'], list)
        
        # Should have at least the root node
        self.assertGreater(len(data['nodes']), 0)
    
    def test_graph_build_invalid_request(self):
        """Test graph build with invalid request"""
        request_data = {
            "refDataType": "Instrument",
            # Missing required fields
        }
        
        response = self.fetch(
            '/api/graph/build',
            method='POST',
            body=json.dumps(request_data),
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.code, 400)
        
        data = json.loads(response.body)
        self.assertIn('error', data)
        self.assertIn('code', data['error'])
        self.assertIn('message', data['error'])
    
    def test_type_resolve_endpoint(self):
        """Test type resolution endpoint"""
        response = self.fetch(
            '/api/resolve-type?refDataType=Instrument&idType=InstrumentId&idValue={"instrumentId":"A125989590"}'
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertIn('genericType', data)
        self.assertIn('specificType', data)
        self.assertIn('resolved', data)
        
        self.assertEqual(data['genericType'], 'Instrument')
        self.assertTrue(data['resolved'])
        self.assertIn(data['specificType'], ['Stock', 'Option', 'Future', 'Bond'])
    
    def test_node_payload_endpoint(self):
        """Test node payload endpoint"""
        response = self.fetch(
            '/api/graph/node/payload?nodeId=A125989590&refDataType=Stock&idType=instrumentId&idValue={"instrumentId":"A125989590"}'
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertIn('nodeId', data)
        self.assertIn('payload', data)
        self.assertEqual(data['nodeId'], 'A125989590')
        self.assertIsInstance(data['payload'], dict)


if __name__ == '__main__':
    unittest.main()
