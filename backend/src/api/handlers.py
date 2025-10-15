"""
API handlers for the financial data relationship explorer.
"""

import tornado.web
import json
from .base_handler import BaseHandler
from src.config.config_manager import ConfigurationManager
from src.services.graph_service import GraphService
from src.services.tree_service import TreeService
from src.data_providers.base_provider import BaseDataProvider
from typing import Dict, Any


class MetadataHandler(BaseHandler):
    """Handler for metadata endpoint"""

    def initialize(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager

    def get(self):
        """Get metadata for reference data types"""
        try:
            metadata = self.config_manager.get_metadata_for_api()
            self.write_json(metadata)
        except Exception as e:
            self.write_error_response("METADATA_ERROR", str(e), 500)


class GraphBuilderHandler(BaseHandler):
    """Handler for graph building endpoint"""

    def initialize(self, graph_service: GraphService):
        self.graph_service = graph_service

    def post(self):
        """Build relationship graph"""
        try:
            data = self.get_json_body()
            self.validate_required_fields(data, ["refDataType", "idType", "idValue"])

            ref_data_type = data["refDataType"]
            id_type = data["idType"]
            id_value = data["idValue"]

            # Optional parameters
            source = data.get("source", "Athena")
            effective_datetime = data.get("effectiveDatetime")

            result = self.graph_service.build_initial_graph(
                ref_data_type,
                id_type,
                id_value,
                source=source,
                effective_datetime=effective_datetime,
            )

            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except ValueError as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("GRAPH_BUILD_ERROR", str(e), 500)


class NodeExpandHandler(BaseHandler):
    """Handler for node expansion endpoint"""

    def initialize(self, graph_service: GraphService):
        self.graph_service = graph_service

    def post(self):
        """Expand relationships from a specific node"""
        try:
            data = self.get_json_body()
            self.validate_required_fields(
                data, ["nodeId", "refDataType", "idType", "idValue"]
            )

            node_id = data["nodeId"]
            ref_data_type = data["refDataType"]
            id_type = data["idType"]
            id_value = data["idValue"]

            result = self.graph_service.expand_node(
                node_id, ref_data_type, id_type, id_value
            )
            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except ValueError as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("NODE_EXPAND_ERROR", str(e), 500)


class NodePayloadHandler(BaseHandler):
    """Handler for node payload endpoint"""

    def initialize(self, data_providers: Dict[str, BaseDataProvider]):
        self.data_providers = data_providers

    def get(self):
        """Get detailed payload for a specific node"""
        try:
            node_id = self.get_argument("nodeId")
            ref_data_type = self.get_argument("refDataType")
            id_type = self.get_argument("idType")
            id_value_str = self.get_argument("idValue")

            # Parse id_value JSON string
            import json

            id_value = json.loads(id_value_str)

            # Get appropriate provider
            provider = self._get_data_provider(ref_data_type)
            entity = provider.get_entity_by_id(ref_data_type, id_type, id_value)

            if not entity:
                self.write_error_response(
                    "NODE_NOT_FOUND", f"Node not found: {node_id}", 404
                )
                return

            result = {"nodeId": node_id, "payload": entity.data}

            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except (ValueError, json.JSONDecodeError) as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("PAYLOAD_ERROR", str(e), 500)

    def _get_data_provider(self, entity_type: str) -> BaseDataProvider:
        """Get appropriate data provider for entity type"""
        provider_map = {
            "Stock": "InstrumentDataProvider",
            "Option": "InstrumentDataProvider",
            "Future": "InstrumentDataProvider",
            "Bond": "InstrumentDataProvider",
            "Listing": "ListingDataProvider",
            "Exchange": "ExchangeDataProvider",
            "InstrumentParty": "PartyDataProvider",
            "Client": "PartyDataProvider",
        }

        provider_name = provider_map.get(entity_type)
        if not provider_name or provider_name not in self.data_providers:
            raise ValueError(f"No data provider found for entity type: {entity_type}")

        return self.data_providers[provider_name]


class TreeBuilderHandler(BaseHandler):
    """Handler for tree-list building endpoint"""

    def initialize(self, tree_service: TreeService):
        self.tree_service = tree_service

    def post(self):
        """Build tree-list view for expensive relationships"""
        try:
            data = self.get_json_body()
            self.validate_required_fields(data, ["refDataType", "idType", "idValue"])

            ref_data_type = data["refDataType"]
            id_type = data["idType"]
            id_value = data["idValue"]

            # Pagination and filtering parameters
            page = data.get("page", 1)
            page_size = data.get("size", 50)

            filters = data.get("filters", {})
            sort_by = data.get("sortBy")

            result = self.tree_service.build_tree_list(
                ref_data_type, id_type, id_value, page, page_size, filters, sort_by
            )

            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except ValueError as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("TREE_BUILD_ERROR", str(e), 500)


class TreeExpandHandler(BaseHandler):
    """Handler for tree item expansion endpoint"""

    def initialize(self, tree_service: TreeService):
        self.tree_service = tree_service

    def post(self):
        """Expand a tree item to show its relationships"""
        try:
            data = self.get_json_body()
            self.validate_required_fields(
                data, ["nodeId", "refDataType", "idType", "idValue"]
            )

            result = self.tree_service.expand_tree_item(data)
            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except ValueError as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("TREE_EXPAND_ERROR", str(e), 500)


class TypeResolveHandler(BaseHandler):
    """Handler for entity type resolution endpoint"""

    def initialize(self, data_providers: Dict[str, BaseDataProvider]):
        self.data_providers = data_providers

    def get(self):
        """Resolve generic type to specific type"""
        try:
            ref_data_type = self.get_argument("refDataType")
            id_type = self.get_argument("idType")
            id_value_str = self.get_argument("idValue")

            # Parse id_value JSON string
            import json

            id_value = json.loads(id_value_str)

            # Try each data provider for type resolution
            resolved_type = None
            for provider in self.data_providers.values():
                try:
                    resolved_type = provider.resolve_entity_type(
                        ref_data_type, id_type, id_value
                    )
                    if resolved_type:
                        break
                except Exception:
                    continue

            result = {
                "genericType": ref_data_type,
                "specificType": resolved_type,
                "resolved": resolved_type is not None,
            }

            self.write_json(result)

        except tornado.web.HTTPError:
            raise
        except (ValueError, json.JSONDecodeError) as e:
            self.write_error_response("INVALID_REQUEST", str(e), 400)
        except Exception as e:
            self.write_error_response("TYPE_RESOLVE_ERROR", str(e), 500)
