# Financial Data Relationship Explorer - Complete Documentation

## 📚 Documentation Index

This project includes comprehensive documentation covering all aspects of the backend service:

### 1. **README.md** - Quick Start Guide
- Project overview
- Installation instructions
- Quick start guide
- Feature highlights

### 2. **docs/API.md** - API Documentation
- Complete REST API reference
- Request/response formats
- Error handling
- Sample curl commands
- Testing instructions

### 3. **docs/ARCHITECTURE.md** - Architecture Guide
- Complete architecture overview
- Layer-by-layer breakdown
- Data flow patterns
- Business domain relationships
- Caching strategy
- Extension points for adding new entities

### 4. **docs/CLASS_DIAGRAM.md** - Detailed Class Diagrams
- Complete class structure with methods and properties
- Dependency graphs
- Method call sequences
- Interaction flows
- Visual UML-like diagrams

## 🎯 Quick Reference

### Project Structure
```
financial-data-explorer/
├── src/                      # Source code
│   ├── entities/            # Entity type classes (Stock, Option, etc.)
│   ├── data_providers/      # Data access layer
│   ├── cache/              # Multi-level caching system
│   ├── services/           # Business logic (GraphBuilder, etc.)
│   ├── config/             # YAML configuration files
│   └── api/                # REST API handlers
├── mock_data/              # Sample JSON data files
├── tests/                  # Unit and integration tests
├── docs/                   # Comprehensive documentation
└── main.py                 # Application entry point
```

### Key Components

#### **Entity Layer**
- **BaseEntity**: Abstract base class for all entities
- **Concrete Entities**: Stock, Option, Future, Bond, Listing, Exchange, InstrumentParty, Client
- **TreeListNode**: Special node for expensive relationships

#### **Data Provider Layer**
- **BaseDataProvider**: Abstract interface with parent node context
- **InstrumentDataProvider**: Handles Stock, Option, Future, Bond
- **ListingDataProvider**: Handles Listing entities
- **ExchangeDataProvider**: Handles Exchange entities
- **PartyDataProvider**: Handles InstrumentParty and Client entities
- **CachedProviderMixin**: Adds automatic caching to any provider

#### **Cache Layer**
- **CacheInterface**: Pluggable cache interface
- **MemoryCache**: Thread-safe in-memory implementation with TTL
- **CacheManager**: High-level cache operations with decorators
- **Multi-level caching**: Entity, Relationship, Graph, Metadata levels

#### **Service Layer**
- **GraphBuilder**: Builds relationship graphs with 2-level depth control
- **GraphService**: Adds caching to graph operations
- **TreeService**: Handles tree-list views for expensive relationships

#### **Configuration Layer**
- **ConfigurationManager**: Loads YAML configs
- **entity_types.yaml**: Entity definitions
- **relationships.yaml**: Relationship definitions

#### **API Layer**
- **BaseHandler**: Common Tornado handler functionality
- **7 REST Endpoints**: Complete API coverage

### Design Patterns Used

1. **Abstract Factory Pattern**
   - `BaseEntity` with `create_entity_instance()` factory method
   - Creates appropriate entity instances based on type

2. **Mixin Pattern**
   - `CachedProviderMixin` adds caching to data providers
   - Multiple inheritance for composable functionality

3. **Strategy Pattern**
   - Different data providers for different entity types
   - Registry pattern for provider management

4. **Decorator Pattern**
   - `@cached_method` decorator for automatic method caching
   - Clean separation of caching concerns

5. **Template Method Pattern**
   - `BaseDataProvider` defines algorithm structure
   - Subclasses implement specific steps

6. **Repository Pattern**
   - Data providers act as repositories
   - Abstract data access logic

### Key Features Implemented

✅ **Two-Level Graph Building** - Always 2 levels, expand on demand  
✅ **Parent Node Context** - Optimization through parent awareness  
✅ **ID-Based Relationships** - Memory-efficient tuple format  
✅ **Multi-Level Caching** - Entity, relationship, and graph caching  
✅ **Type Resolution** - Generic to specific type conversion  
✅ **Configuration-Driven** - YAML-based extensibility  
✅ **Tree-List Views** - Pagination for expensive relationships  
✅ **Comprehensive Error Handling** - Proper HTTP status codes  
✅ **Thread Safety** - Thread-safe cache implementation  
✅ **Best Practices** - SOLID principles, clean architecture  

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup tests
python test_setup.py

# Start the server
python main.py

# Or use the start script
python start.py

# Run unit tests
pytest tests/

# Server runs on
http://localhost:8888
```

### Sample API Calls

```bash
# Get metadata
curl http://localhost:8888/api/meta

# Build graph for Apple stock
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Instrument",
    "idType": "InstrumentId",
    "idValue": {"instrumentId": "A125989590"}
  }'

# Expand a node
curl -X POST http://localhost:8888/api/graph/node/expand \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "A125989590",
    "refDataType": "Stock",
    "idType": "instrumentId",
    "idValue": {"instrumentId": "A125989590"}
  }'

# Get node payload
curl "http://localhost:8888/api/graph/node/payload?nodeId=A125989590&refDataType=Stock&idType=instrumentId&idValue=%7B%22instrumentId%22%3A%22A125989590%22%7D"

# Resolve type
curl "http://localhost:8888/api/resolve-type?refDataType=Instrument&idType=InstrumentId&idValue=%7B%22instrumentId%22%3A%22A125989590%22%7D"
```

### Adding New Entity Types

To add a new entity type (e.g., "ETF"), follow these steps:

1. **Create Entity Class** in `src/entities/entity_types.py`:
```python
class ETF(BaseEntity):
    def _get_primary_id(self) -> str:
        return self.data.get('etfId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('etf_type', 'ETF'),
            "titleLine2": self.data.get('name', ''),
            # ... other fields
        }
```

2. **Add Configuration** in `src/config/entity_types.yaml`:
```yaml
specific_entities:
  ETF:
    parent_type: "Instrument"
    display_config:
      title_line1_field: "etf_type"
      title_line2_field: "name"
    data_source:
      provider: "InstrumentDataProvider"
      method: "get_etf_by_id"
```

3. **Define Relationships** in `src/config/relationships.yaml`:
```yaml
relationships:
  ETF:
    - name: "HAS_LISTING"
      target_type: "Listing"
      cardinality: "1:many"
```

4. **Update Data Provider** in `src/data_providers/instrument_provider.py`:
```python
def get_entity_by_id(self, entity_type, ...):
    if entity_type == "ETF":
        data = self._get_etf_data(id_value.get('etfId'))
        return self.create_entity_instance('ETF', data)

def _get_etf_data(self, etf_id: str) -> Optional[Dict]:
    etfs = self.mock_data.get('etfs', [])
    for etf in etfs:
        if etf.get('etfId') == etf_id:
            return etf
    return None
```

5. **Update Factory** in `src/data_providers/base_provider.py`:
```python
entity_classes = {
    ...
    'ETF': ETF
}
```

6. **Add Mock Data** in `mock_data/instruments.json`:
```json
{
  "etfs": [
    {
      "etfId": "ETF-001",
      "name": "S&P 500 ETF",
      "etf_type": "Equity ETF",
      "status": "ACTIVE"
    }
  ]
}
```

That's it! The new entity type is now fully integrated.

### Performance Characteristics

#### Cache Hit Rates (Expected)
- **Entity Cache**: ~80-90% (entities are frequently re-accessed)
- **Relationship Cache**: ~70-80% (relationships queried multiple times)
- **Graph Cache**: ~60-70% (repeated queries for same entities)

#### Response Times (Expected)
- **Graph Build (uncached)**: 50-200ms (depending on complexity)
- **Graph Build (cached)**: <10ms
- **Node Expansion (uncached)**: 20-100ms
- **Node Expansion (cached)**: <5ms
- **Metadata Retrieval**: <5ms (always fast)

#### Memory Usage
- **Entity Cache**: ~1KB per entity (varies by type)
- **Relationship Cache**: ~100 bytes per relationship
- **Graph Cache**: ~10-50KB per graph (varies by size)
- **Total Memory**: Scales with cache size and TTL settings

### Testing Coverage

The project includes comprehensive tests:

- **Unit Tests**: Entity types, cache system
- **Integration Tests**: API endpoints, full workflows
- **Setup Tests**: Verify installation and configuration

Run tests with:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_entities.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Troubleshooting

#### Common Issues

1. **ImportError: No module named 'tornado'**
   - Solution: `pip install -r requirements.txt`

2. **FileNotFoundError: mock_data/instruments.json**
   - Solution: Ensure you're running from project root directory

3. **Port 8888 already in use**
   - Solution: Set environment variable `PORT=9999` or kill process on 8888

4. **Cache not working**
   - Check: `cache_manager.is_enabled()` should return `True`
   - Enable: `cache_manager.enable()`

5. **Type resolution failing**
   - Ensure entity exists in mock data
   - Check that entity ID matches exactly

### Production Considerations

When moving to production:

1. **Replace Mock Data Providers**
   - Implement database-backed data providers
   - Keep same interface as `BaseDataProvider`

2. **Use Redis for Caching**
   - Implement `CacheInterface` for Redis
   - Shared cache across multiple instances

3. **Add Authentication/Authorization**
   - Implement JWT or OAuth2
   - Add user context to requests

4. **Enable Logging**
   - Add structured logging throughout
   - Use ELK stack or similar for log aggregation

5. **Add Monitoring**
   - Prometheus metrics for cache hit rates
   - APM for performance monitoring
   - Health check endpoints

6. **Load Balancing**
   - Multiple Tornado instances behind load balancer
   - Session affinity not required (stateless)

7. **Database Connection Pooling**
   - Use connection pools for database access
   - Configure timeouts and retry logic

### Support and Contribution

For questions or issues:
1. Check documentation in `docs/` folder
2. Review architecture diagrams
3. Run test suite to verify setup
4. Check API documentation for endpoint details

### License

This project is designed for internal use in financial data management systems.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Python Version**: 3.8+  
**Framework**: Tornado 6.3.3
