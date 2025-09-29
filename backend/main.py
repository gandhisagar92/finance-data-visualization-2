"""
Main application entry point for the Financial Data Relationship Explorer.
"""

import tornado.web
import tornado.ioloop
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config.config_manager import ConfigurationManager
from data_providers.registry import DataProviderRegistry
from cache.cache_manager import CacheManager
from services.graph_builder import GraphBuilder
from services.graph_service import GraphService
from services.tree_service import TreeService
from api.handlers import (
    MetadataHandler,
    GraphBuilderHandler,
    NodeExpandHandler,
    NodePayloadHandler,
    TreeBuilderHandler,
    TreeExpandHandler,
    TypeResolveHandler,
)


def create_application():
    """Create and configure the Tornado application"""

    # Initialize configuration manager
    config_dir = os.path.join(os.path.dirname(__file__), "src", "config")
    config_manager = ConfigurationManager(config_dir)

    # Initialize cache manager
    cache_manager = CacheManager()

    # Initialize data provider registry
    data_provider_registry = DataProviderRegistry()

    # Initialize providers with configuration
    provider_configs = {
        "InstrumentDataProvider": {},
        "ListingDataProvider": {},
        "ExchangeDataProvider": {},
        "PartyDataProvider": {},
    }
    data_provider_registry.initialize_all_providers(provider_configs, cache_manager)

    # Get all providers
    data_providers = data_provider_registry.get_all_providers()

    # Initialize services
    graph_builder = GraphBuilder(config_manager, data_providers)
    graph_service = GraphService(graph_builder, cache_manager)
    tree_service = TreeService(data_providers, config_manager)

    # Define URL routes
    handlers = [
        (r"/api/meta", MetadataHandler, {"config_manager": config_manager}),
        (r"/api/graph/build", GraphBuilderHandler, {"graph_service": graph_service}),
        (
            r"/api/graph/node/expand",
            NodeExpandHandler,
            {"graph_service": graph_service},
        ),
        (
            r"/api/graph/node/payload",
            NodePayloadHandler,
            {"data_providers": data_providers},
        ),
        (r"/api/build/tree", TreeBuilderHandler, {"tree_service": tree_service}),
        (r"/api/tree/item/expand", TreeExpandHandler, {"tree_service": tree_service}),
        (r"/api/resolve-type", TypeResolveHandler, {"data_providers": data_providers}),
    ]

    # Create application
    settings = {"debug": True, "autoreload": True}

    return tornado.web.Application(handlers, **settings)


def main():
    """Main function to start the server"""
    print("Starting Financial Data Relationship Explorer...")

    try:
        # Create application
        app = create_application()

        # Configure server
        port = int(os.environ.get("PORT", 8888))
        app.listen(port)

        print(f"Server started on http://localhost:{port}")
        print("Available endpoints:")
        print(f"  GET  http://localhost:{port}/api/meta")
        print(f"  POST http://localhost:{port}/api/graph/build")
        print(f"  POST http://localhost:{port}/api/graph/node/expand")
        print(f"  GET  http://localhost:{port}/api/graph/node/payload")
        print(f"  POST http://localhost:{port}/api/build/tree")
        print(f"  POST http://localhost:{port}/api/tree/item/expand")
        print(f"  GET  http://localhost:{port}/api/resolve-type")
        print("\nPress Ctrl+C to stop the server")

        # Start the server
        tornado.ioloop.IOLoop.current().start()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
