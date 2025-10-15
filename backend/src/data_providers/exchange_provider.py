"""
Exchange data provider implementation.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_provider import BaseDataProvider
from entities.entity_types import Entity
import json
import os


class ExchangeDataProvider(BaseDataProvider):
    """Data provider for Exchange entities"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._data = self._load_data()
        print(f"ExchangeDataProvider initialized with {len(self._data)} exchanges.")

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load exchange data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "exchanges.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("exchanges", [])
        except FileNotFoundError:
            print(f"Warning: exchanges.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing exchanges.json: {e}")
            return []

    def get_entity_by_id(
        self,
        entity_type: str,
        id_type: str,
        id_value: Dict[str, Any],
        parent_node: Optional[Entity] = None,
        relationship: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Entity]:
        """Get exchange entity by identifier"""

        for exchange in self._data:
            if id_type == "exchangeId" and exchange.get("exchangeId") == id_value.get(
                "exchangeId"
            ):
                return self._create_entity_from_data(exchange, **kwargs)
            elif id_type == "mic" and exchange.get("mic") == id_value.get("mic"):
                return self._create_entity_from_data(exchange, **kwargs)

        return None

    def _create_entity_from_data(
        self, exchange_data: Dict[str, Any], **kwargs
    ) -> Entity:
        """Create Entity object from exchange data"""
        transformed_data = {
            "id": exchange_data.get("exchangeId"),
            "exchangeId": exchange_data.get("exchangeId"),
            "titleLine1": exchange_data.get("exchangeId", ""),
            "titleLine2": f"{exchange_data.get('description', '')} {exchange_data.get('currency', '')}",
            "status": exchange_data.get("status", "UNKNOWN"),
            "mic": exchange_data.get("mic"),
            "idType": "exchangeId",
            "idValue": {"exchangeId": exchange_data.get("exchangeId")},
            "effectiveDate": kwargs.get("as_of", ""),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": False,
        }

        return Entity(
            data=transformed_data, entity_type="Exchange", display_type="graph-node"
        )

    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get IDs of related entities"""
        # Exchange doesn't have outgoing relationships in current model
        return []
