"""
Instrument data provider implementation.
Handles data retrieval for Stock, Option, Future, and Bond entities.
"""

from .base_provider import BaseDataProvider
from .cached_provider_mixin import CachedProviderMixin
from entities.entity_types import BaseEntity
from typing import List, Dict, Any, Optional, Tuple
import json
import os
from datetime import datetime


class InstrumentDataProvider(CachedProviderMixin, BaseDataProvider):
    """Data provider for instrument-related entities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config=config)
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON files"""
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        mock_data_path = os.path.join(project_root, 'mock_data', 'instruments.json')
        
        try:
            with open(mock_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return empty data structure if file doesn't exist
            return {
                'stocks': [],
                'options': [],
                'futures': [],
                'bonds': [],
                'listings': []
            }
    
    def get_entity_by_id(self, entity_type: str, id_type: str, 
                        id_value: Dict[str, Any], 
                        parent_node: Optional[BaseEntity] = None, 
                        **kwargs) -> Optional[BaseEntity]:
        """Get instrument entity by ID with parent context"""
        
        # Use parent context for optimization or validation if needed
        if parent_node:
            # Example: Validate that option belongs to the parent stock
            if entity_type == "Option" and parent_node.entity_type == "Stock":
                # Additional validation logic here
                pass
        
        if entity_type == "Stock":
            data = self._get_stock_data(id_value.get('instrumentId'))
            return self.create_entity_instance('Stock', data) if data else None
            
        elif entity_type == "Option":
            data = self._get_option_data(id_value.get('instrumentId'))
            return self.create_entity_instance('Option', data) if data else None
            
        elif entity_type == "Future":
            data = self._get_future_data(id_value.get('instrumentId'))
            return self.create_entity_instance('Future', data) if data else None
            
        elif entity_type == "Bond":
            data = self._get_bond_data(id_value.get('instrumentId'))
            return self.create_entity_instance('Bond', data) if data else None
            
        elif entity_type == "Listing":
            data = self._get_listing_data(id_value.get('tradingLineId'))
            return self.create_entity_instance('Listing', data) if data else None
            
        return None
    
    def _get_stock_data(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        """Get raw stock data by instrument ID"""
        stocks = self.mock_data.get('stocks', [])
        for stock in stocks:
            if stock.get('instrumentId') == instrument_id:
                return stock
        return None
    
    def _get_option_data(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        """Get raw option data by instrument ID"""
        options = self.mock_data.get('options', [])
        for option in options:
            if option.get('instrumentId') == instrument_id:
                return option
        return None
    
    def _get_future_data(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        """Get raw future data by instrument ID"""
        futures = self.mock_data.get('futures', [])
        for future in futures:
            if future.get('instrumentId') == instrument_id:
                return future
        return None
    
    def _get_bond_data(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        """Get raw bond data by instrument ID"""
        bonds = self.mock_data.get('bonds', [])
        for bond in bonds:
            if bond.get('instrumentId') == instrument_id:
                return bond
        return None
    
    def _get_listing_data(self, trading_line_id: str) -> Optional[Dict[str, Any]]:
        """Get raw listing data by trading line ID"""
        listings = self.mock_data.get('listings', [])
        for listing in listings:
            if listing.get('tradingLineId') == trading_line_id:
                return listing
        return None
    
    def get_related_entity_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs based on relationship"""
        
        if relationship_name == "HAS_LISTING" and source_entity.entity_type in ["Stock", "Option", "Future", "Bond"]:
            return self._get_instrument_listing_ids(source_entity.id)
            
        elif relationship_name == "IS_UNDERLYING_FOR" and source_entity.entity_type == "Stock":
            return self._get_options_by_underlying_ids(source_entity.id, **kwargs)
            
        elif relationship_name == "HAS_UNDERLYING" and source_entity.entity_type == "Option":
            underlying_id = source_entity.underlying_instrument_id
            if underlying_id:
                return [("instrumentId", underlying_id)]
                
        elif relationship_name == "HAS_UNDERLYING_ASSET" and source_entity.entity_type == "Future":
            underlying_id = source_entity.underlying_asset_id
            if underlying_id:
                return [("instrumentId", underlying_id)]
        
        return []
    
    def _get_instrument_listing_ids(self, instrument_id: str) -> List[Tuple[str, str]]:
        """Get listing IDs for an instrument"""
        listings = self.mock_data.get('listings', [])
        result = []
        for listing in listings:
            if listing.get('instrumentId') == instrument_id:
                result.append(("tradingLineId", listing.get('tradingLineId')))
        return result
    
    def _get_options_by_underlying_ids(self, underlying_id: str, 
                                     page: int = 1, page_size: int = 50,
                                     filters: Dict = None) -> List[Tuple[str, str]]:
        """Get option IDs by underlying instrument"""
        options = self.mock_data.get('options', [])
        filtered_options = [
            opt for opt in options 
            if opt.get('underlyingInstrumentId') == underlying_id
        ]
        
        # Apply filters if provided
        if filters:
            filtered_options = self._apply_filters(filtered_options, filters)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_options = filtered_options[start_idx:end_idx]
        
        return [("instrumentId", opt.get('instrumentId')) for opt in paginated_options]
    
    def _apply_filters(self, items: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to item list"""
        filtered_items = items
        
        for field, value in filters.items():
            if field == 'optionType' and value:
                filtered_items = [
                    item for item in filtered_items 
                    if item.get('optionType') == value
                ]
            elif field == 'expirationDate' and isinstance(value, dict):
                # Date range filter
                from_date = value.get('from')
                to_date = value.get('to')
                if from_date or to_date:
                    filtered_items = [
                        item for item in filtered_items
                        if self._date_in_range(item.get('expirationDate'), 
                                             from_date, to_date)
                    ]
        
        return filtered_items
    
    def _date_in_range(self, date_str: str, from_date: str, to_date: str) -> bool:
        """Check if date is within range"""
        if not date_str:
            return False
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if from_date:
                from_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                if date_obj < from_obj:
                    return False
            
            if to_date:
                to_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                if date_obj > to_obj:
                    return False
            
            return True
        except ValueError:
            return False
    
    def resolve_entity_type(self, generic_type: str, id_type: str, 
                          id_value: Dict[str, Any]) -> Optional[str]:
        """Resolve instrument type"""
        if generic_type != "Instrument":
            return None
            
        instrument_id = id_value.get('instrumentId')
        if not instrument_id:
            return None
        
        # Check in stocks first
        if self._get_stock_data(instrument_id):
            return "Stock"
        
        # Check in options
        if self._get_option_data(instrument_id):
            return "Option"
            
        # Check in futures
        if self._get_future_data(instrument_id):
            return "Future"
            
        # Check in bonds
        if self._get_bond_data(instrument_id):
            return "Bond"
        
        return None
