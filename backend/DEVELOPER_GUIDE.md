# Developer Quick Reference

## Common Development Tasks

### Running the Application
```bash
# Run tests first
python test_setup.py

# Start the server
python main.py

# The API will be available at http://localhost:8888
```

### Testing API Endpoints

#### 1. Get Metadata
```bash
curl http://localhost:8888/api/meta
```

#### 2. Build Graph for a Stock
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Stock",
    "idType": "instrumentId",
    "idValue": {"instrumentId": "STK-100"}
  }'
```

#### 3. Expand a Node
```bash
curl -X POST http://localhost:8888/api/graph/node/expand \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "STK-100",
    "refDataType": "Stock",
    "idType": "instrumentId",
    "idValue": {"instrumentId": "STK-100"}
  }'
```

#### 4. Get Node Payload
```bash
curl "http://localhost:8888/api/graph/node/payload?nodeId=STK-100&refDataType=Stock&idType=instrumentId&idValue=%7B%22instrumentId%22:%22STK-100%22%7D"
```

## Code Organization

### Where to Find Things

| Task | Location |
|------|----------|
| Add new entity type | `src/config/entity_definition.py` |
| Add new relationship | `src/config/relationship_definition.py` |
| Create data provider | `src/data_providers/` (new file) |
| Modify graph logic | `src/services/graph_builder.py` |
| Add API endpoint | `src/api/handlers.py` |
| Change cache behavior | `src/cache/` |
| Mock data | `mock_data/*.json` |

### File Responsibilities

```
entity_definition.py    → Display templates for each entity
relationship_definition.py → Relationship configs
config_manager.py      → Loads and provides configs
entity_types.py        → Base Entity class with transformation
base_provider.py       → Data provider interface
*_provider.py          → Entity-specific data access
provider_registry.py   → Registers all providers
graph_builder.py       → Core graph building logic
graph_service.py       → Graph operations + caching
handlers.py            → API endpoints
```

## Data Flow

### Building a Graph
```
API Request
    ↓
GraphBuilderHandler
    ↓
GraphService (checks cache)
    ↓
GraphBuilder.build_graph()
    ↓
DataProvider.get_entity_by_id()  ← Fetches root entity
    ↓
DataProvider.get_related_entity_ids()  ← Gets related IDs
    ↓
DataProvider.get_entity_by_id()  ← Fetches related entities
    ↓
Entity.to_graph_node_dict()  ← Transforms to API format
    ↓
Response with nodes and edges
```

### Entity Transformation
```
Raw Data (from JSON/DB)
    ↓
DataProvider creates Entity object
    ↓
Entity.data contains structured data
    ↓
ConfigManager provides entity_definition
    ↓
Entity.to_graph_node_dict(entity_definition)
    ↓
Applies template with ${field} placeholders
    ↓
Returns formatted node dict for API
```

## Common Patterns

### Creating a New Data Provider

```python
from .base_provider import BaseDataProvider
from entities.entity_types import Entity

class MyEntityProvider(BaseDataProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._data = self._load_data()
    
    def _load_data(self):
        # Load from JSON/DB
        pass
    
    def get_entity_by_id(self, entity_type, id_type, id_value, **kwargs):
        # Find and return entity
        # Handle expensive relationships by returning placeholders
        pass
    
    def get_related_entity_ids(self, source_entity, relationship, **kwargs):
        # Return list of (id_type, id_value) tuples
        pass
```

### Defining Entity Template

```python
"MyEntity": {
    "header": {
        "id": "${id}",
        "titleLine1": "${title}",
        "titleLine2": "${name}",
        "status": "${status}",
    },
    "footer": {
        "refDataType": "MyEntity",
        "idType": "${idType}",
        "idValue": {"${idValue.key}": "${idValue.value}"},
    },
    "body": {
        "graph-node": {
            "additionalLines": {
                "Field 1": "${field1}",
                "Field 2": "${field2}",
            }
        }
    }
}
```

### Defining Relationships

```python
"MyEntity": [
    {
        "name": "HAS_RELATED",
        "targetType": "RelatedEntity",
        "cardinality": "1:n",
        "label": "RELATED",
        "expensive": False
    }
]
```

## Debugging Tips

### Enable Verbose Logging
```python
# In main.py, set debug=True
tornado.web.Application([...], debug=True)
```

### Test Individual Components
```python
# Test configuration
from src.config.config_manager import ConfigurationManager
config = ConfigurationManager()
print(config.get_entity_definition("Stock"))

# Test data provider
from src.data_providers.provider_registry import DataProviderRegistry
registry = DataProviderRegistry()
stock_provider = registry.get_provider("Stock")
stock = stock_provider.get_entity_by_id("Stock", "instrumentId", {"instrumentId": "STK-100"})
print(stock.data)

# Test graph builder
from src.services.graph_builder import GraphBuilder
builder = GraphBuilder(config, registry.get_all_providers())
graph = builder.build_graph("Stock", "instrumentId", {"instrumentId": "STK-100"})
print(f"Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
```

### Check Cache
```python
# Check if caching is working
from src.cache.cache_manager import CacheManager
from src.cache.memory_cache import MemoryCache

cache_mgr = CacheManager(MemoryCache())
cache_mgr.set("test_key", {"data": "test"}, ttl=60)
print(cache_mgr.get("test_key"))  # Should print the data
```

## Performance Considerations

### Caching Strategy
- **Graph results**: 5 minutes TTL
- **Node expansion**: 3 minutes TTL
- **Tree lists**: No cache (data changes frequently)

### Expensive Relationships
- Mark relationships as `"expensive": True`
- Return placeholder nodes instead of fetching all data
- User clicks to load tree-list with pagination

### Optimization Tips
1. Add indexes on ID fields in database
2. Use connection pooling for DB access
3. Implement query result caching in data providers
4. Consider Redis for distributed caching
5. Add pagination for all list results

## Troubleshooting

### "No provider found for entity type"
- Check `provider_registry.py` - is the provider registered?
- Verify the entity type name matches exactly (case-sensitive)

### "Missing required fields" error
- Check API request body has all required fields
- Verify field names match exactly

### Empty graph returned
- Check if entity exists in mock data
- Verify ID type and value are correct
- Check data provider implementation

### Template placeholders not replaced
- Verify field exists in entity.data
- Check template syntax: `${fieldName}`
- For nested fields: `${parent.child}`

### Circular relationships causing issues
- Add visited tracking in graph builder
- Limit max depth appropriately
- Consider breaking circular refs in relationship definitions

## Best Practices

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public methods
- Keep functions focused and small

### Configuration
- Never hard-code entity data in methods
- Use templates for all display formatting
- Keep relationship logic in data providers
- Centralize configs in definition files

### Testing
- Run `test_setup.py` before committing
- Test API endpoints manually after changes
- Verify graph structure and edge relationships
- Check performance with large datasets

### Commits
- Make atomic commits for each feature
- Write clear commit messages
- Test before committing
- Update documentation with code changes
