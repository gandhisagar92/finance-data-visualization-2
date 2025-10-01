"""
Tree service for handling tree-list operations.
"""

from typing import Dict, Any, List, Optional
from data_providers.base_provider import BaseDataProvider
from config.config_manager import ConfigurationManager
import json
import os


class TreeService:
    """Service for tree-list operations"""
    
    def __init__(self, data_provider_registry: Dict[str, BaseDataProvider], 
                 config_manager: ConfigurationManager):
        self.data_providers = data_provider_registry
        self.config_manager = config_manager
        self._all_options_data = None
    
    def _load_all_options(self) -> List[Dict[str, Any]]:
        """Load all options from all_options.json file"""
        if self._all_options_data is not None:
            return self._all_options_data
        
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        all_options_path = os.path.join(project_root, 'mock_data', 'all_options.json')
        
        try:
            with open(all_options_path, 'r') as f:
                data = json.load(f)
                self._all_options_data = data.get('value', [])
                return self._all_options_data
        except FileNotFoundError:
            print(f"Warning: all_options.json not found at {all_options_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing all_options.json: {e}")
            return []
    
    def build_tree_list(self, ref_data_type: str, id_type: str, 
                       id_value: Dict[str, Any], 
                       page: int = 1, page_size: int = 50,
                       filters: Optional[Dict] = None, 
                       sort_by: Optional[str] = None) -> Dict[str, Any]:
        """Build paginated tree-list for expensive relationships"""
        
        # Special handling for Options with underlyingInstrumentId
        if ref_data_type == "Option" and id_type == "underlyingInstrumentId":
            return self._build_options_tree_list(id_value, page, page_size, filters, sort_by)
        
        # Default implementation for other types
        provider = self._get_data_provider(ref_data_type)
        return self._build_paginated_tree(
            provider, ref_data_type, id_type, id_value, 
            page, page_size, filters, sort_by
        )
    
    def _build_options_tree_list(self, id_value: Dict[str, Any], 
                                 page: int, page_size: int,
                                 filters: Optional[Dict], 
                                 sort_by: Optional[str]) -> Dict[str, Any]:
        """Build tree list for options filtered by underlying instrument"""
        
        # Get source entity ID and relationship name
        source_entity_id = id_value.get('sourceEntityId')
        relationship_name = id_value.get('relationshipName', 'IS_UNDERLYING_FOR')
        
        if not source_entity_id:
            return self._empty_tree_response(page, page_size)
        
        # Load all options from file
        all_options = self._load_all_options()
        
        # Filter options by underlying instrument ID
        filtered_options = []
        for option in all_options:
            underlyings = option.get('underlyings', [])
            for underlying in underlyings:
                if underlying.get('instrumentId') == source_entity_id:
                    filtered_options.append(option)
                    break
        
        # Apply additional filters if provided
        if filters:
            filtered_options = self._apply_filters(filtered_options, filters)
        
        # Apply sorting
        if sort_by:
            filtered_options = self._apply_sorting(filtered_options, sort_by)
        
        # Calculate pagination
        total_items = len(filtered_options)
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page of data
        page_options = filtered_options[start_idx:end_idx]
        
        # Transform to response format
        data = []
        for option in page_options:
            data.append(self._transform_option_to_row(option))
        
        # Get column configuration from relationships.yaml
        meta = self._get_tree_list_meta(relationship_name)
        
        return {
            "data": data,
            "page": page,
            "size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "meta": meta
        }
    
    def _transform_option_to_row(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Transform option data to row format with all required fields"""
        
        # Extract option-specific fields
        option_details = option.get('option', {})
        strike_info = option_details.get('strike', {})
        
        # Get primary trading line
        trading_lines = option.get('tradingLines', [])
        primary_trading_line = None
        primary_timing_rule = None
        
        # Find first active trading line as primary
        for tl in trading_lines:
            if tl.get('status') == 'ACTIVE':
                primary_trading_line = tl.get('tradingLineId')
                primary_timing_rule = tl.get('timingRule', '')
                break
        
        # If no active, take first one
        if not primary_trading_line and trading_lines:
            primary_trading_line = trading_lines[0].get('tradingLineId')
            primary_timing_rule = trading_lines[0].get('timingRule', '')
        
        return {
            "instrumentId": option.get('instrumentId'),
            "name": option.get('name'),
            "status": option.get('status'),
            "isin": option.get('isin'),
            "postTradeId": option.get('postTradeId'),
            "strike_price": strike_info.get('price'),
            "contractSize": option.get('contractSize'),
            "putOrCall": option_details.get('putOrCall'),
            "expirationDate": option_details.get('expirationDate'),
            "exerciseStyle": option_details.get('exerciseStyle'),
            "primaryTradingLine": primary_trading_line,
            "timingRule": primary_timing_rule
        }
    
    def _get_tree_list_meta(self, relationship_name: str) -> Dict[str, Any]:
        """Get column metadata from relationships.yaml configuration"""
        
        # For IS_UNDERLYING_FOR relationship on Stock entity
        relationships = self.config_manager.get_entity_relationships('Stock')
        
        for rel in relationships:
            if rel.get('name') == relationship_name:
                tree_config = rel.get('tree_list_config', {})
                return {
                    "columns": tree_config.get('columns', []),
                    "column_groups": tree_config.get('column_groups', [])
                }
        
        # Default empty meta if not found
        return {"columns": [], "column_groups": []}
    
    def _apply_filters(self, options: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to options list"""
        filtered = options
        
        for field, value in filters.items():
            if field == 'status' and value:
                filtered = [opt for opt in filtered if opt.get('status') == value]
            elif field == 'putOrCall' and value:
                filtered = [opt for opt in filtered 
                           if opt.get('option', {}).get('putOrCall') == value]
            elif field == 'expirationDate' and isinstance(value, dict):
                from_date = value.get('from')
                to_date = value.get('to')
                if from_date or to_date:
                    filtered = [opt for opt in filtered
                               if self._date_in_range(
                                   opt.get('option', {}).get('expirationDate'),
                                   from_date, to_date
                               )]
        
        return filtered
    
    def _apply_sorting(self, options: List[Dict], sort_by: str) -> List[Dict]:
        """Apply sorting to options list"""
        # Parse sort_by format: "field:asc" or "field:desc"
        parts = sort_by.split(':')
        field = parts[0]
        direction = parts[1] if len(parts) > 1 else 'asc'
        reverse = (direction == 'desc')
        
        if field == 'expirationDate':
            return sorted(options, 
                         key=lambda x: x.get('option', {}).get('expirationDate', ''),
                         reverse=reverse)
        elif field == 'strike_price':
            return sorted(options,
                         key=lambda x: x.get('option', {}).get('strike', {}).get('price', 0),
                         reverse=reverse)
        elif field == 'instrumentId':
            return sorted(options,
                         key=lambda x: x.get('instrumentId', ''),
                         reverse=reverse)
        elif field == 'name':
            return sorted(options,
                         key=lambda x: x.get('name', ''),
                         reverse=reverse)
        
        return options
    
    def _date_in_range(self, date_str: str, from_date: str, to_date: str) -> bool:
        """Check if date is within range"""
        if not date_str:
            return False
        
        try:
            from datetime import datetime
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
    
    def _empty_tree_response(self, page: int, page_size: int) -> Dict[str, Any]:
        """Return empty tree response"""
        return {
            "data": [],
            "page": page,
            "size": page_size,
            "total_items": 0,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "meta": {"columns": [], "column_groups": []}
        }
    
    def expand_tree_item(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Expand a tree item to show its immediate relationships"""
        ref_data_type = node_data.get('refDataType')
        id_type = node_data.get('idType')
        id_value = node_data.get('idValue', {})
        
        if not all([ref_data_type, id_type, id_value]):
            raise ValueError("Invalid node data for tree expansion")
        
        provider = self._get_data_provider(ref_data_type)
        entity = provider.get_entity_by_id(ref_data_type, id_type, id_value)
        
        if not entity:
            return {'items': [], 'pagination': {}}
        
        # Get relationships and convert to tree format
        relationships = self.config_manager.get_entity_relationships(entity.entity_type)
        items = []
        
        for relationship in relationships:
            if not relationship.get('display_in_graph', True):
                continue
                
            try:
                related_ids = provider.get_related_entity_ids(entity, relationship['name'])
                
                for id_type_rel, id_value_rel in related_ids:
                    target_provider = self._get_data_provider(relationship['target_type'])
                    target_entity = target_provider.get_entity_by_id(
                        relationship['target_type'], id_type_rel, {id_type_rel: id_value_rel}
                    )
                    
                    if target_entity:
                        items.append({
                            'id': target_entity.id,
                            'columns': self._entity_to_columns(target_entity),
                            'expandable': len(self.config_manager.get_entity_relationships(target_entity.entity_type)) > 0,
                            'refDataType': target_entity.entity_type,
                            'idType': id_type_rel,
                            'idValue': {id_type_rel: id_value_rel}
                        })
            except Exception as e:
                print(f"Error expanding tree item for relationship {relationship['name']}: {e}")
                continue
        
        return {
            'items': items,
            'pagination': {
                'page': 1,
                'pageSize': len(items),
                'totalItems': len(items),
                'totalPages': 1,
                'hasNext': False,
                'hasPrevious': False
            }
        }
    
    def _build_paginated_tree(self, provider: BaseDataProvider, 
                            ref_data_type: str, id_type: str, id_value: Dict[str, Any],
                            page: int, page_size: int, 
                            filters: Optional[Dict], sort_by: Optional[str]) -> Dict[str, Any]:
        """Build paginated tree structure"""
        # For now, return empty structure
        # In a real implementation, this would handle complex tree building with pagination
        return {
            'items': [],
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'totalItems': 0,
                'totalPages': 0,
                'hasNext': False,
                'hasPrevious': False
            }
        }
    
    def _entity_to_columns(self, entity) -> Dict[str, Any]:
        """Convert entity to column format for tree display"""
        # Create a simplified column view of the entity
        columns = {
            'id': entity.id,
            'type': entity.entity_type,
            'status': entity.get_field_value('status') or 'UNKNOWN'
        }
        
        # Add entity-specific columns
        if entity.entity_type == 'Stock':
            columns.update({
                'name': entity.get_field_value('name'),
                'isin': entity.get_field_value('isin'),
                'sector': entity.get_field_value('sector')
            })
        elif entity.entity_type == 'Option':
            columns.update({
                'name': entity.get_field_value('name'),
                'optionType': entity.get_field_value('optionType'),
                'strike': entity.get_field_value('strike'),
                'expirationDate': entity.get_field_value('expirationDate')
            })
        elif entity.entity_type == 'Listing':
            columns.update({
                'ric': entity.get_field_value('ric'),
                'bloombergTicker': entity.get_field_value('bloombergTicker'),
                'exchangeId': entity.get_field_value('exchangeId')
            })
        
        return columns
    
    def _get_data_provider(self, entity_type: str) -> BaseDataProvider:
        """Get appropriate data provider for entity type"""
        provider_map = {
            'Stock': 'InstrumentDataProvider',
            'Option': 'InstrumentDataProvider',
            'Future': 'InstrumentDataProvider',
            'Bond': 'InstrumentDataProvider',
            'Listing': 'ListingDataProvider',
            'Exchange': 'ExchangeDataProvider',
            'InstrumentParty': 'PartyDataProvider',
            'Client': 'PartyDataProvider'
        }
        
        provider_name = provider_map.get(entity_type)
        if not provider_name:
            raise ValueError(f"No data provider found for entity type: {entity_type}")
        
        if provider_name not in self.data_providers:
            raise ValueError(f"Data provider not registered: {provider_name}")
        
        return self.data_providers[provider_name]
