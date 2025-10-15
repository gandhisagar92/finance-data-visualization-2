"""
Listing data provider implementation.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_provider import BaseDataProvider
from entities.entity_types import Entity
import json
import os


class ListingDataProvider(BaseDataProvider):
    """Data provider for Listing entities"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._data = self._load_data()
        print(f"ListingDataProvider initialized with {len(self._data)} listings.")

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load listing data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "listings.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("listings", [])
        except FileNotFoundError:
            print(f"Warning: listings.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing listings.json: {e}")
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
        """Get listing entity by identifier"""

        for listing in self._data:
            if id_type == "tradingLineId" and listing.get(
                "tradingLineId"
            ) == id_value.get("tradingLineId"):
                return self._create_entity_from_data(listing, **kwargs)
            elif id_type == "ric" and listing.get("ric") == id_value.get("ric"):
                return self._create_entity_from_data(listing, **kwargs)
            elif id_type == "sedol" and listing.get("sedol") == id_value.get("sedol"):
                return self._create_entity_from_data(listing, **kwargs)

        return None

    def _create_entity_from_data(
        self, listing_data: Dict[str, Any], **kwargs
    ) -> Entity:
        """Create Entity object from listing data"""
        transformed_data = {
            "id": listing_data.get("tradingLineId"),
            "tradingLineId": listing_data.get("tradingLineId"),
            "titleLine1": "Trading Line",
            "titleLine2": "",
            "status": listing_data.get("status", "UNKNOWN"),
            "ric": listing_data.get("ric"),
            "sedol": listing_data.get("sedol"),
            "bloombergTicker": listing_data.get("bloombergTicker"),
            "currency": listing_data.get("currency"),
            "exchangeId": listing_data.get("exchangeId"),
            "idType": "tradingLineId",
            "idValue": {"tradingLineId": listing_data.get("tradingLineId")},
            "effectiveDate": kwargs.get(
                "as_of", listing_data.get("lastUpdatedTimestamp", "")
            ),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": True,
        }

        return Entity(
            data=transformed_data, entity_type="Listing", display_type="graph-node"
        )

    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get IDs of related entities"""
        relationship_name = relationship.get("name")

        if relationship_name == "LISTED_ON":
            return self._get_exchange_ids(source_entity)

        return []

    def _get_exchange_ids(
        self, source_entity: Entity
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get exchange ID for a listing"""
        trading_line_id = source_entity.data.get("tradingLineId")

        for listing in self._data:
            if listing.get("tradingLineId") == trading_line_id:
                exchange_id = listing.get("exchangeId")
                if exchange_id:
                    return [("exchangeId", {"exchangeId": exchange_id})]

        return []
