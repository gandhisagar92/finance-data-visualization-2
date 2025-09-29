"""
Base handler class with common functionality for all API handlers.
"""

import tornado.web
import json
from typing import Dict, Any, Optional


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common functionality"""
    
    def set_default_headers(self):
        """Set CORS headers"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Content-Type", "application/json")
    
    def options(self):
        """Handle OPTIONS requests for CORS"""
        self.set_status(204)
        self.finish()
    
    def write_json(self, data: Dict[str, Any]):
        """Write JSON response"""
        self.write(json.dumps(data, indent=2))
    
    def write_error_response(self, error_code: str, message: str, 
                           status_code: int = 400, details: Optional[Dict] = None):
        """Write standardized error response"""
        error_response = {
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            error_response["error"]["details"] = details
        
        self.set_status(status_code)
        self.write_json(error_response)
    
    def get_json_body(self) -> Dict[str, Any]:
        """Parse JSON request body"""
        try:
            if self.request.body:
                return json.loads(self.request.body)
            return {}
        except json.JSONDecodeError as e:
            raise tornado.web.HTTPError(400, f"Invalid JSON: {str(e)}")
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list):
        """Validate that required fields are present"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise tornado.web.HTTPError(
                400, f"Missing required fields: {', '.join(missing_fields)}"
            )
