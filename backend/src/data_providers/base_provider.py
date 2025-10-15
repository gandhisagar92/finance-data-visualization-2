"""
Base data provider interface.
Defines the contract for all data providers in the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Avoid circular import by importing at function level when needed
from entities.entity_types import Entity


class BaseDataProvider(ABC):
    """Base class for all data providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def get_entity_by_id(
        self,
        entity_type: str,
        id_type: str,
        id_value: Dict[str, Any],
        parent_node: Optional[Entity] = None,
        relationship: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Entity]:
        """Get a single entity by its identifier with optional parent context"""
        """
        sample input arguments:
        For root node (Stock):
            entity_type = "Stock"
            id_type = "instrumentId"
            id_value = {"instrumentId": "STK-100"}
            parent_node = None
            relationship = None
            kwargs = {"as_of": datetime(2023, 1, 1, 12, 0, 45), "source": "Bloomberg"}

        For related node (Listing):
            entity_type = "Listing"
            id_type = "tradingLineId"
            id_value = {"tradingLineId": "TL-1001"}
            parent_node = <Stock instance> # instance of BaseEntity (Stock)
            relationship = {"name": "HAS_LISTING", "targetType": "Listing", "cardinality": "1:n", "label": "LISTING", "expensive": False}
            kwargs = {"as_of": datetime(2023, 1, 1, 12, 0, 45), "source": "Bloomberg"}

        This method is overridden by each data provider implementation to fetch entity data from its source.
        It fetches the entity of the specified type using the given identifier. Use json files from /mock_data/ folder for mock data.
        The method should return an instance of the requested entity type populated with data, or None if not found.

        Note: For expensive relationships, the respective data provider may choose to return a minimal entity with only id populated.
        For example, OptionDataProvider - for Stock with relationship "IS_UNDERLYING_FOR" may fetch data as follows:
        if relationship["expensive"] is True:
            generate data as follows:
            data = {
                "id": "Options_With_Stock_Underlying_100",
                "titleLine1": "Click to view all Options",
                "refDataType": "Option",
                "idType": "Underlying",
                "idValue": {"underlyingInstrumentId": "STK-100"},
                "asOf": "2025-09-24T12:00:00",
                "source": "Bloomberg",
                "expandable": "true",
            }
            return Entity(data=data, entity_type="Option", type="graph-node")
        else:
            fetch full data for Option entity as usual.

        """
        pass

    @abstractmethod
    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get related entity IDs as list of [(idType, {idValue.key: idValue.value})] tuples"""
        """
        sample input arguments:
        source_entity = <Stock instance> # instance of Entity (Stock)
        relationship = {"name": "HAS_LISTING", "targetType": "Listing", "cardinality": "1:n", "label": "LISTING", "expensive": False}
        kwargs = {"as_of": datetime(2023, 1, 1, 12, 0, 45), "source": "Bloomberg"}

        This method is overridden by each data provider implementation to fetch related entity IDs from its source.
        It fetches the IDs of entities related to the given source entity via the specified relationship.
        The method should return a list of tuples, each containing the id_type and id_value of a related entity.
        For example: [("tradingLineId", {"tradingLineId": "TL-1001"}), ("tradingLineId", {"tradingLineId": "TL-1002"})]
        Or
        [("economics", {"underlyingInstrumentId": "STK-100", "strikePrice": 150.0, "expirationDate": "2023-12-31"})]
        Or return an empty list if no related entities are found.

        Note, for expensive relationships, the respective data provider may choose to return list as stated below:
        StockDataProvider for relationship "IS_UNDERLYING_FOR" may return:
        [("Underlying", {"instrumentId": "STK-100"})]

        """
        pass

    def resolve_entity_type(
        self, generic_type: str, id_type: str, id_value: Dict[str, Any]
    ) -> Optional[str]:
        """Resolve generic type to specific type"""
        """
        This method is not overridden by any of the child data provider classes.
        Make this method as static if possible.
        For example, if generic_type is "Instrument", id_type is "economics" and id_value is {"underlyingInstrumentId": "STK-100", "strikePrice": 150.0, "expirationDate": "2023-12-31"},
        the method should return "Option" as the specific type.

        For testing, make this method return "Stock" for any input.
        """
        return "Stock"
