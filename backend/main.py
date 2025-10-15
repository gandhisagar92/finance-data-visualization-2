"""
Main application entry point.
"""

import tornado.web
import tornado.ioloop
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.api.handlers import (
    MetadataHandler,
    GraphBuilderHandler,
    NodeExpandHandler,
    NodePayloadHandler,
    TreeBuilderHandler,
    TreeExpandHandler,
    TypeResolveHandler,
)
from src.config.config_manager import ConfigurationManager
from src.data_providers.provider_registry import DataProviderRegistry
from services.graph_builder import GraphBuilder
from services.graph_service import GraphService
from services.tree_service import TreeService
from cache.cache_manager import CacheManager
from cache.memory_cache import MemoryCache


def make_app():
    """Create and configure the Tornado application"""

    # Initialize core components
    config_manager = ConfigurationManager()
    provider_registry = DataProviderRegistry()
    data_providers = provider_registry.get_all_providers()

    # Initialize services
    graph_builder = GraphBuilder(config_manager, data_providers)
    cache_manager = CacheManager(MemoryCache())
    graph_service = GraphService(graph_builder, cache_manager)
    tree_service = TreeService(data_providers, config_manager)

    # Define routes
    return tornado.web.Application(
        [
            (r"/api/meta", MetadataHandler, dict(config_manager=config_manager)),
            (
                r"/api/graph/build",
                GraphBuilderHandler,
                dict(graph_service=graph_service),
            ),
            (
                r"/api/graph/node/expand",
                NodeExpandHandler,
                dict(graph_service=graph_service),
            ),
            (
                r"/api/graph/node/payload",
                NodePayloadHandler,
                dict(data_providers=data_providers),
            ),
            (r"/api/tree/build", TreeBuilderHandler, dict(tree_service=tree_service)),
            (
                r"/api/tree/item/expand",
                TreeExpandHandler,
                dict(tree_service=tree_service),
            ),
            (
                r"/api/type/resolve",
                TypeResolveHandler,
                dict(data_providers=data_providers),
            ),
        ],
        debug=True,
    )


def main():
    """Main application entry point"""
    app = make_app()
    port = 8888

    print(f"Starting Financial Data Relationship Explorer on port {port}...")
    print(f"API endpoints:")
    print(f"  - GET  http://localhost:{port}/api/meta")
    print(f"  - POST http://localhost:{port}/api/graph/build")
    print(f"  - POST http://localhost:{port}/api/graph/node/expand")
    print(f"  - GET  http://localhost:{port}/api/graph/node/payload")
    print(f"  - POST http://localhost:{port}/api/tree/build")
    print(f"  - POST http://localhost:{port}/api/tree/item/expand")
    print(f"  - GET  http://localhost:{port}/api/type/resolve")
    print(f"\nPress Ctrl+C to stop the server")

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
