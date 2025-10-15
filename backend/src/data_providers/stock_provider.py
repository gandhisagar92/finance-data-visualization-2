"""
Stock data provider implementation.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_provider import BaseDataProvider
from entities.entity_types import Entity
import json
import os


class StockDataProvider(BaseDataProvider):
    """Data provider for Stock entities"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._data = self._load_data()
        print(f"StockDataProvider initialized with {len(self._data)} stocks.")

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load stock data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "stocks.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("stocks", [])
        except FileNotFoundError:
            print(f"Warning: stocks.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing stocks.json: {e}")
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
        """Get stock entity by identifier"""

        # Handle expensive relationship  - return placeholder
        if relationship and relationship.get("expensive", False):
            # Count total options for this stock
            option_count = self._count_options_for_stock(id_value.get("instrumentId"))

            placeholder_data = {
                "id": f"{id_value.get('instrumentId')}_AS_UNDERLYING",
                "titleLine1": "Click to view all Options",
                "titleLine2": "",
                "status": "ACTIVE",
                "additionalLines": {"Total Count": str(option_count)},
                "refDataType": "Option",
                "idType": "underlyingInstrumentId",
                "idValue": {"underlyingInstrumentId": id_value.get("instrumentId")},
                "displayType": "tree-list",
                "isFurtherExpandable": False,
            }

            return Entity(
                data=placeholder_data, entity_type="Option", display_type="graph-node"
            )

        # Regular entity fetch
        for stock in self._data:
            if id_type == "instrumentId" and stock.get("instrumentId") == id_value.get(
                "instrumentId"
            ):
                return self._create_entity_from_data(stock, **kwargs)
            elif id_type == "isin" and stock.get("isin") == id_value.get("isin"):
                return self._create_entity_from_data(stock, **kwargs)
            elif id_type == "ric":
                # Search in trading lines
                for tl in stock.get("tradingLines", []):
                    if tl.get("ric") == id_value.get("ric"):
                        return self._create_entity_from_data(stock, **kwargs)

        return None

    def _create_entity_from_data(self, stock_data: Dict[str, Any], **kwargs) -> Entity:
        """Create Entity object from stock data"""
        # Transform data for entity
        transformed_data = {
            "id": stock_data.get("instrumentId"),
            "instrumentId": stock_data.get("instrumentId"),
            "titleLine1": stock_data.get("assetClassifications", {})
            .get("bloomberg", {})
            .get("securityType", "Stock"),
            "titleLine2": stock_data.get("name", ""),
            "status": stock_data.get("status", "UNKNOWN"),
            "isin": stock_data.get("isin"),
            "sector": stock_data.get("assetClassifications", {})
            .get("bloomberg", {})
            .get("marketSector", ""),
            "idType": "instrumentId",
            "idValue": {"instrumentId": stock_data.get("instrumentId")},
            "effectiveDate": kwargs.get(
                "as_of", stock_data.get("lastUpdatedTimestamp")
            ),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": True,
            "payload": stock_data,
        }

        return Entity(
            data=transformed_data, entity_type="Stock", display_type="graph-node"
        )

    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get IDs of related entities"""
        relationship_name = relationship.get("name")

        if relationship_name == "HAS_LISTING":
            return self._get_listing_ids(source_entity)
        elif relationship_name == "HAS_ISSUER":
            return self._get_issuer_ids(source_entity)
        elif relationship_name == "IS_UNDERLYING_FOR":
            # For expensive relationship, return placeholder reference
            return [
                (
                    "underlyingInstrumentId",
                    {"underlyingInstrumentId": source_entity.data.get("instrumentId")},
                )
            ]

        return []

    def _get_listing_ids(
        self, source_entity: Entity
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get trading line IDs for a stock"""
        instrument_id = source_entity.data.get("instrumentId")

        for stock in self._data:
            if stock.get("instrumentId") == instrument_id:
                result = []
                for tl in stock.get("tradingLines", []):
                    result.append(
                        ("tradingLineId", {"tradingLineId": tl.get("tradingLineId")})
                    )
                return result

        return []

    def _get_issuer_ids(
        self, source_entity: Entity
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get issuer IDs for a stock"""
        instrument_id = source_entity.data.get("instrumentId")

        for stock in self._data:
            if stock.get("instrumentId") == instrument_id:
                issuer = stock.get("issuer", {})
                i_party_id = issuer.get("iPartyId")
                if i_party_id:
                    return [("entityId", {"entityId": i_party_id})]

        return []

    def _count_options_for_stock(self, instrument_id: str) -> int:
        """Count options where this stock is underlying"""
        # Load options data
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        options_path = os.path.join(current_dir, "mock_data", "options.json")

        try:
            with open(options_path, "r") as f:
                data = json.load(f)
                options = data.get("options", [])

                count = 0
                for option in options:
                    underlyings = option.get("underlyings", [])
                    for underlying in underlyings:
                        if underlying.get("instrumentId") == instrument_id:
                            count += 1
                            break

                return count
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
