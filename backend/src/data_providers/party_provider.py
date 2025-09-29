"""
Party data provider implementation.
Handles data retrieval for InstrumentParty and Client entities.
"""

from .base_provider import BaseDataProvider
from .cached_provider_mixin import CachedProviderMixin
from entities.entity_types import BaseEntity
from typing import List, Dict, Any, Optional, Tuple
import json
import os


class PartyDataProvider(CachedProviderMixin, BaseDataProvider):
    """Data provider for party-related entities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config=config)
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON files"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        mock_data_path = os.path.join(project_root, 'mock_data', 'parties.json')
        
        try:
            with open(mock_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'instrumentParties': [], 'clients': []}
    
    def get_entity_by_id(self, entity_type: str, id_type: str, 
                        id_value: Dict[str, Any], 
                        parent_node: Optional[BaseEntity] = None, 
                        **kwargs) -> Optional[BaseEntity]:
        """Get party entity by ID"""
        
        if entity_type == "InstrumentParty":
            data = self._get_instrument_party_data(id_value.get('instrumentPartyId'))
            return self.create_entity_instance('InstrumentParty', data) if data else None
            
        elif entity_type == "Client":
            data = self._get_client_data(id_value.get('clientId'))
            return self.create_entity_instance('Client', data) if data else None
            
        return None
    
    def _get_instrument_party_data(self, party_id: str) -> Optional[Dict[str, Any]]:
        """Get raw instrument party data by party ID"""
        parties = self.mock_data.get('instrumentParties', [])
        for party in parties:
            if party.get('instrumentPartyId') == party_id:
                return party
        return None
    
    def _get_client_data(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get raw client data by client ID"""
        clients = self.mock_data.get('clients', [])
        for client in clients:
            if client.get('clientId') == client_id:
                return client
        return None
    
    def get_related_entity_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs based on relationship"""
        
        if relationship_name == "HAS_ENTITY" and source_entity.entity_type == "InstrumentParty":
            client_id = source_entity.get_field_value('clientId')
            if client_id:
                return [("clientId", client_id)]
        
        return []
    
    def resolve_entity_type(self, generic_type: str, id_type: str, 
                          id_value: Dict[str, Any]) -> Optional[str]:
        """Resolve entity type"""
        # Parties are not generic types in this model
        return None
