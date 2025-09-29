"""
Base data provider interface.
Defines the contract for all data providers in the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Avoid circular import by importing at function level when needed
from entities.entity_types import BaseEntity, Stock, Option, Future, Bond, Listing, Exchange, InstrumentParty, Client


class BaseDataProvider(ABC):
    """Base class for all data providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    def get_entity_by_id(self, entity_type: str, id_type: str, 
                        id_value: Dict[str, Any], 
                        parent_node: Optional[BaseEntity] = None, 
                        **kwargs) -> Optional[BaseEntity]:
        """Get a single entity by its identifier with optional parent context"""
        pass
        
    @abstractmethod
    def get_related_entity_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs as list of (id_type, id_value) tuples"""
        pass
        
    @abstractmethod
    def resolve_entity_type(self, generic_type: str, id_type: str, 
                          id_value: Dict[str, Any]) -> Optional[str]:
        """Resolve generic type to specific type"""
        pass
    
    def create_entity_instance(self, entity_type: str, data: Dict[str, Any]) -> BaseEntity:
        """Factory method to create entity instances"""
        entity_classes = {
            'Stock': Stock,
            'Option': Option,
            'Future': Future,
            'Bond': Bond,
            'Listing': Listing,
            'Exchange': Exchange,
            'InstrumentParty': InstrumentParty,
            'Client': Client
        }
        
        entity_class = entity_classes.get(entity_type)
        if not entity_class:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        return entity_class(data)
