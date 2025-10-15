"""
Party data provider implementation for InstrumentParty and Client entities.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_provider import BaseDataProvider
from entities.entity_types import Entity
import json
import os


class PartyDataProvider(BaseDataProvider):
    """Data provider for InstrumentParty and Client entities"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._instrument_parties = self._load_instrument_parties()
        self._clients = self._load_clients()
        print(
            f"PartyDataProvider initialized with {len(self._instrument_parties)} instrument parties and {len(self._clients)} clients."
        )

    def _load_instrument_parties(self) -> List[Dict[str, Any]]:
        """Load instrument party data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "instrumentparties.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("clients", [])  # Note: file has "clients" key
        except FileNotFoundError:
            print(f"Warning: instrumentparties.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing instrumentparties.json: {e}")
            return []

    def _load_clients(self) -> List[Dict[str, Any]]:
        """Load client data from JSON file"""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        data_path = os.path.join(current_dir, "mock_data", "clients.json")

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                return data.get("clients", [])
        except FileNotFoundError:
            print(f"Warning: clients.json not found at {data_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing clients.json: {e}")
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
        """Get party entity by identifier"""

        if entity_type == "InstrumentParty":
            for party in self._instrument_parties:
                if id_type == "entityId" and party.get("entityId") == id_value.get(
                    "entityId"
                ):
                    return self._create_instrument_party_entity(party, **kwargs)
                elif id_type == "eci" and party.get("eci") == id_value.get("eci"):
                    return self._create_instrument_party_entity(party, **kwargs)

        elif entity_type == "Client":
            for client in self._clients:
                if id_type == "entityId" and client.get("entityId") == id_value.get(
                    "entityId"
                ):
                    return self._create_client_entity(client, **kwargs)
                elif id_type == "eci" and client.get("eci") == id_value.get("eci"):
                    return self._create_client_entity(client, **kwargs)
                elif id_type == "spn" and client.get("spn") == id_value.get("spn"):
                    return self._create_client_entity(client, **kwargs)

        return None

    def _create_instrument_party_entity(
        self, party_data: Dict[str, Any], **kwargs
    ) -> Entity:
        """Create Entity object for InstrumentParty"""
        transformed_data = {
            "id": f"IPARTY-{party_data.get('entityId')}",
            "entityId": party_data.get("entityId"),
            "titleLine1": "Instrument Party",
            "titleLine2": party_data.get("name", ""),
            "status": party_data.get("status", "UNKNOWN"),
            "eci": party_data.get("eci"),
            "spn": party_data.get("spn"),
            "lei": party_data.get("lei"),
            "idType": "entityId",
            "idValue": {"entityId": party_data.get("entityId")},
            "effectiveDate": kwargs.get("as_of", ""),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": True,
        }

        return Entity(
            data=transformed_data,
            entity_type="InstrumentParty",
            display_type="graph-node",
        )

    def _create_client_entity(self, client_data: Dict[str, Any], **kwargs) -> Entity:
        """Create Entity object for Client"""
        transformed_data = {
            "id": f"CLIENT-{client_data.get('entityId')}",
            "entityId": client_data.get("entityId"),
            "titleLine1": "Party",
            "titleLine2": client_data.get("name", ""),
            "status": client_data.get("status", "UNKNOWN"),
            "eci": client_data.get("eci"),
            "spn": client_data.get("spn"),
            "lei": client_data.get("lei"),
            "idType": "eci",
            "idValue": {"eci": client_data.get("eci")},
            "effectiveDate": kwargs.get("as_of", ""),
            "source": kwargs.get("source", "Athena"),
            "isFurtherExpandable": False,
        }

        return Entity(
            data=transformed_data, entity_type="Client", display_type="graph-node"
        )

    def get_related_entity_ids(
        self, source_entity: Entity, relationship: Dict[str, Any], **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get IDs of related entities"""
        relationship_name = relationship.get("name")

        if relationship_name == "PARTY_OF":
            return self._get_client_ids(source_entity)

        return []

    def _get_client_ids(
        self, source_entity: Entity
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Get client ID for an instrument party"""
        entity_id = source_entity.data.get("entityId")

        for party in self._instrument_parties:
            if party.get("entityId") == entity_id:
                # Return the same entity as client (based on data structure)
                eci = party.get("eci")
                if eci:
                    return [("eci", {"eci": eci})]

        return []
