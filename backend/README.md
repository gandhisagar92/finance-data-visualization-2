# Financial Data Relationship Explorer

A Python web application for visualizing relationships between financial reference data entities in an interactive, graphical format.

## Architecture Overview

The application follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Tornado)                     │
│  handlers.py - REST endpoints for graph, tree, metadata     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Service Layer                             │
│  ├─ GraphService - Manages graph operations with caching    │
│  ├─ GraphBuilder - Core graph building framework            │
│  └─ TreeService - Handles tree-list operations              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Data Provider Layer                         │
│  ├─ StockDataProvider                                        │
│  ├─ ListingDataProvider                                      │
│  ├─ ExchangeDataProvider                                     │
│  ├─ PartyDataProvider                                        │
│  └─ OptionDataProvider                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Configuration & Entities                        │
│  ├─ ConfigManager - Manages entity & relationship configs   │
│  ├─ Entity - Base entity with transformation logic          │
│  ├─ entity_definition.py - Entity display templates         │
│  └─ relationship_definition.py - Relationship configs        │
└──────────────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. **Separation of Concerns**
- **API Layer**: Handles HTTP requests/responses
- **Service Layer**: Business logic for graph/tree operations
- **Data Provider Layer**: Data access abstraction
- **Configuration Layer**: Centralized entity and relationship definitions

### 2. **Framework vs Entity Code**
- **Core Framework** (graph_builder.py, graph_service.py): Generic graph traversal logic that doesn't change
- **Entity Code** (data providers, definitions): Specific to each entity type, easy to add new ones

### 3. **Easy Extensibility**
To add a new entity type:
1. Add entity definition to `entity_definition.py`
2. Add relationships to `relationship_definition.py`
3. Create a data provider class (extends BaseDataProvider)
4. Register in `provider_registry.py`
5. Add metadata to `meta.yaml`

The core graph building logic remains unchanged!

## Project Structure

```
financial-data-explorer/
├── main.py                          # Application entry point
├── test_setup.py                    # Component tests
├── requirements.txt                 # Python dependencies
├── mock_data/                       # JSON data files
│   ├── stocks.json
│   ├── listings.json
│   ├── exchanges.json
│   ├── options.json
│   ├── instrumentparties.json
│   └── clients.json
└── src/
    ├── api/                         # API handlers
    │   ├── base_handler.py
    │   └── handlers.py
    ├── cache/                       # Caching layer
    │   ├── cache_interface.py
    │   ├── cache_manager.py
    │   └── memory_cache.py
    ├── config/                      # Configuration
    │   ├── config_manager.py        # Configuration manager
    │   ├── entity_definition.py     # Entity display templates
    │   ├── relationship_definition.py  # Relationship configs
    │   └── meta.yaml                # API metadata
    ├── data_providers/              # Data access layer
    │   ├── base_provider.py         # Base provider interface
    │   ├── stock_provider.py
    │   ├── listing_provider.py
    │   ├── exchange_provider.py
    │   ├── party_provider.py
    │   ├── option_provider.py
    │   └── provider_registry.py
    ├── entities/                    # Entity types
    │   └── entity_types.py          # Base Entity class
    └── services/                    # Business logic
        ├── graph_builder.py         # Core graph building
        ├── graph_service.py         # Graph operations with cache
        └── tree_service.py          # Tree-list operations
```

## Core Components

### Entity Class
- Base class for all entity types
- Handles data transformation using templates from entity_definition.py
- Converts entity data to API response format
- No hard-coded entity-specific logic

### Data Providers
- One provider per entity type (or related group)
- Implements `get_entity_by_id()` and `get_related_entity_ids()`
- Handles data fetching and relationship traversal
- Currently uses JSON files, easily replaceable with database calls

### Configuration Manager
- Centralized management of entity definitions and relationships
- Loads configurations from Python modules and YAML
- Provides metadata for API endpoints
- Single source of truth for entity structures

### Graph Builder
- Core framework for graph construction
- Traverses relationships recursively up to specified depth
- Handles expensive relationships (returns placeholders)
- Generic logic that works for any entity type

### Graph Service
- High-level graph operations
- Integrates caching for performance
- Provides build and expand operations

## API Endpoints

### GET /api/meta
Returns metadata about all entity types and their queryable ID types.

### POST /api/graph/build
Builds a graph starting from a root entity, traversing up to 2 levels deep.

**Request:**
```json
{
  "refDataType": "Stock",
  "idType": "instrumentId",
  "idValue": {"instrumentId": "STK-100"},
  "source": "Athena",
  "effectiveDatetime": "2024-01-15 00:00:00"
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "STK-100",
      "titleLine1": "Common Stock",
      "titleLine2": "Company 1",
      "status": "ACTIVE",
      "additionalLines": {...},
      "refDataType": "Stock",
      "idType": "instrumentId",
      "idValue": {"instrumentId": "STK-100"},
      "asOf": "2025-09-24T12:00:00",
      "expandable": true
    }
  ],
  "edges": [
    {
      "source": "STK-100",
      "target": "TL-1001",
      "relationship": "LISTING"
    }
  ]
}
```

### POST /api/graph/node/expand
Expands a specific node by loading its relationships.

### GET /api/graph/node/payload
Returns the complete data payload for a node.

### POST /api/tree/build
Builds a tree-list view for expensive relationships (with pagination).

### POST /api/tree/item/expand
Expands a tree item to show its relationships.

### GET /api/type/resolve
Resolves generic types to specific types (e.g., "Instrument" -> "Stock").

## Expensive Relationships

For relationships that would return too many results (e.g., all Options for a Stock):
- A placeholder node is returned with displayType="tree-list"
- Clicking the placeholder calls the tree-list API
- Tree-list supports pagination, filtering, and sorting

## Adding a New Entity Type

Example: Adding a "Bond" entity type

1. **Add entity definition** (`config/entity_definition.py`):
```python
"Bond": {
    "header": {
        "id": "${id}",
        "titleLine1": "${titleLine1}",
        "titleLine2": "${titleLine2}",
        "status": "${status}",
    },
    "footer": {...},
    "body": {
        "graph-node": {
            "additionalLines": {
                "ISIN": "${isin}",
                "Maturity": "${maturityDate}",
            }
        }
    }
}
```

2. **Add relationships** (`config/relationship_definition.py`):
```python
"Bond": [
    {
        "name": "HAS_ISSUER",
        "targetType": "InstrumentParty",
        "cardinality": "1:1",
        "label": "ISSUER",
        "expensive": False
    }
]
```

3. **Create data provider** (`data_providers/bond_provider.py`):
```python
class BondDataProvider(BaseDataProvider):
    def get_entity_by_id(self, ...):
        # Fetch bond data
        
    def get_related_entity_ids(self, ...):
        # Return related entity IDs
```

4. **Register provider** (`data_providers/provider_registry.py`):
```python
self._providers["Bond"] = BondDataProvider(self.config)
```

5. **Add metadata** (`config/meta.yaml`):
```yaml
entities:
  Bond:
    description: "Fixed income instruments"
    specific_types:
      - Bond
    id_types:
      ISIN:
        inputs:
          - id: "isin"
            label: "ISIN"
            kind: "text"
```

That's it! The core framework will handle the rest.

## Running the Application

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
python test_setup.py
```

### Start Server
```bash
python main.py
```

The server will start on `http://localhost:8888`

## Testing the API

### Get Metadata
```bash
curl http://localhost:8888/api/meta
```

### Build a Graph
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Stock",
    "idType": "instrumentId",
    "idValue": {"instrumentId": "STK-100"}
  }'
```

## Technology Stack

- **Python 3.x**
- **Tornado** - Web framework
- **PyYAML** - Configuration parsing
- **JSON** - Data storage (mock)

## Future Enhancements

- Replace JSON files with actual database connections
- Add Redis for distributed caching
- Implement graph cycle detection
- Add graph visualization UI
- Support for custom relationship filters
- Real-time graph updates via WebSockets
