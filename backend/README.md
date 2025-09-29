# Financial Data Relationship Explorer - Backend Service

A Python-based web service for visualizing relationships between financial reference data entities using Tornado web framework.

## Features

- Interactive graph visualization of financial data relationships
- Support for multiple entity types (Stock, Option, Future, Bond, etc.)
- Configurable relationship definitions
- Multi-level caching system
- REST API endpoints for graph building and navigation
- Tree-list views for expensive relationships
- Pluggable data providers

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python src/main.py
```

3. Access the API at `http://localhost:8888`

## API Endpoints

- `GET /api/meta` - Get metadata for reference data types
- `POST /api/graph/build` - Build relationship graph
- `POST /api/graph/node/expand` - Expand specific node
- `GET /api/graph/node/payload` - Get node payload
- `POST /api/build/tree` - Build tree-list view
- `POST /api/tree/item/expand` - Expand tree item
- `GET /api/resolve-type` - Resolve entity type

## Architecture

The service follows a clean architecture with the following layers:
- **API Layer**: Tornado handlers for REST endpoints
- **Service Layer**: Business logic and graph building
- **Data Layer**: Entity management and data providers
- **Cache Layer**: Multi-level caching system
- **Config Layer**: Configuration management

## Configuration

Entity types and relationships are defined in YAML files in the `src/config` directory.
