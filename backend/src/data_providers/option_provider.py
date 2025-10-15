"""
Option data provider implementation.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_provider import BaseDataProvider
from entities.entity_types import Entity
import json
import os


class OptionDataProvider(BaseDataProvider):
    """Data provider for Option entities"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._data = self._load_data()
        print(f"OptionDataProvider initialized with {len(self._data)} options.")

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load option data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "options.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("options", [])
        except FileNotFoundError:
            print(f"Warning: options.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing options.json: {e}")
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
        """Get option entity by identifier"""

        for option in self._data:
            if id_type == "instrumentId" and option.get("instrumentId") == id_value.get(
                "instrumentId"
            ):
                return self._create_entity_from_data(option, **kwargs)
            elif id_type == "isin" and option.get("isin") == id_value.get("isin"):
                return self._create_entity_from_data(option, **kwargs)

        if (
            id_type == "underlyingInstrumentId"
            and relationship
            and relationship.get("expensive", False)
        ):
            transformed_expensive_data = {
                "id": f"{id_value.get('underlyingInstrumentId')}-AS_UNDERLYING",
                "instrumentId": id_value.get("underlyingInstrumentId"),
                "titleLine1": "Click to view all Options",
                "refDataType": "Option",
                "idType": "underlyingInstrumentId",
                "idValue": {
                    "underlyingInstrumentId": id_value.get("underlyingInstrumentId")
                },
                "effectiveDate": kwargs.get("as_of", ""),
                "source": kwargs.get("source", "Athena"),
                "isFurtherExpandable": True,
            }
            return Entity(
                data=transformed_expensive_data,
                entity_type="Option",
                display_type="graph-node",
            )
        return None

    def _create_entity_from_data(self, option_data: Dict[str, Any], **kwargs) -> Entity:
        """Create Entity object from option data"""
        option_details = option_data.get("option", {})

        transformed_data = {
            "id": option_data.get("instrumentId"),
            "instrumentId": option_data.get("instrumentId"),
            "titleLine1": f"{option_details.get('putOrCall', 'Option')}",
            "titleLine2": option_data.get("name", ""),
            "status": option_data.get("status", "UNKNOWN"),
            "isin": option_data.get("isin"),
            "occSymbol": option_details.get("occSymbol", ""),
            "putOrCall": option_details.get("putOrCall"),
            "strikePrice": option_details.get("strike", {}).get("price"),
            "expirationDate": option_details.get("expirationDate"),
            "idType": "instrumentId",
            "idValue": {"instrumentId": option_data.get("instrumentId")},
            "effectiveDate": kwargs.get(
                "as_of", option_data.get("lastUpdatedTimestamp", "")
            ),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": True,
        }

        return Entity(
            data=transformed_data, entity_type="Option", display_type="graph-node"
        )

    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get IDs of related entities"""
        relationship_name = relationship.get("name")

        if relationship_name == "HAS_LISTING":
            return self._get_listing_ids(source_entity)

        return []

    def _get_listing_ids(
        self, source_entity: Entity
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get trading line IDs for an option"""
        instrument_id = source_entity.data.get("instrumentId")

        for option in self._data:
            if option.get("instrumentId") == instrument_id:
                result = []
                for tl in option.get("tradingLines", []):
                    result.append(
                        ("tradingLineId", {"tradingLineId": tl.get("tradingLineId")})
                    )
                return result

        return []
