# Entity Relationship Diagram - Financial Data Explorer

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION ENTRY POINT                         │
│                                main.py                                  │
└────────────┬────────────────────────────────────────────────────────────┘
             │ initializes & orchestrates
             ├──────────┬──────────┬──────────┬──────────┬────────────┐
             ▼          ▼          ▼          ▼          ▼            ▼
┌─────────────────┐ ┌─────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐
│ Configuration   │ │Cache│ │ Data     │ │ Graph   │ │  Tree    │ │  API   │
│ Manager         │ │Mgr  │ │ Provider │ │ Service │ │ Service  │ │Handlers│
└─────────────────┘ └─────┘ │ Registry │ └─────────┘ └──────────┘ └────────┘
                            └──────────┘
```

## Layer Dependencies (Top to Bottom)

### 1. API Layer (Tornado Handlers)
```
BaseHandler (Abstract)
├── MetadataHandler
│   └── uses: ConfigurationManager
├── GraphBuilderHandler
│   └── uses: GraphService
├── NodeExpandHandler
│   └── uses: GraphService
├── NodePayloadHandler
│   └── uses: DataProviderRegistry
├── TreeBuilderHandler
│   └── uses: TreeService
├── TreeExpandHandler
│   └── uses: TreeService
└── TypeResolveHandler
    └── uses: DataProviderRegistry
```

### 2. Service Layer
```
GraphService
├── uses: GraphBuilder
└── uses: CacheManager

GraphBuilder
├── uses: ConfigurationManager
├── uses: DataProviderRegistry
├── creates: BaseEntity instances
└── creates: TreeListNode

TreeService
├── uses: DataProviderRegistry
└── uses: ConfigurationManager
```

### 3. Data Provider Layer
```
BaseDataProvider (Abstract)
├── defines: get_entity_by_id(entity_type, id_type, id_value, parent_node)
├── defines: get_related_entity_ids(source_entity, relationship_name)
├── defines: resolve_entity_type(generic_type, id_type, id_value)
└── provides: create_entity_instance(entity_type, data)

CachedProviderMixin (Mixin)
├── uses: CacheManager
├── provides: get_cached_entity()
├── provides: get_cached_related_ids()
└── provides: cache key generation methods

InstrumentDataProvider
├── inherits: BaseDataProvider
├── mixes: CachedProviderMixin
├── manages: Stock, Option, Future, Bond, Listing
└── implements: all abstract methods

ListingDataProvider
├── inherits: BaseDataProvider
├── mixes: CachedProviderMixin
├── manages: Listing entities
└── implements: all abstract methods

ExchangeDataProvider
├── inherits: BaseDataProvider
├── mixes: CachedProviderMixin
├── manages: Exchange entities
└── implements: all abstract methods

PartyDataProvider
├── inherits: BaseDataProvider
├── mixes: CachedProviderMixin
├── manages: InstrumentParty, Client entities
└── implements: all abstract methods

DataProviderRegistry
├── manages: all provider instances
├── provides: lazy initialization
└── provides: provider lookup by name
```

### 4. Entity Layer
```
BaseEntity (Abstract)
├── properties:
│   ├── data: Dict[str, Any]
│   ├── id: str
│   └── entity_type: str
├── abstract methods:
│   ├── _get_primary_id() -> str
│   └── to_node_dict() -> Dict[str, Any]
└── concrete methods:
    └── get_field_value(field_name) -> Any

Stock (extends BaseEntity)
├── properties:
│   ├── instrument_id: str
│   ├── name: str
│   └── isin: str
└── relationships:
    ├── HAS_LISTING -> Listing (1:many)
    ├── HAS_ISSUER -> InstrumentParty (1:1)
    └── IS_UNDERLYING_FOR -> Option (1:many, expensive)

Option (extends BaseEntity)
├── properties:
│   └── underlying_instrument_id: str
└── relationships:
    ├── HAS_LISTING -> Listing (1:many)
    └── HAS_UNDERLYING -> Stock (1:1)

Future (extends BaseEntity)
├── properties:
│   ├── underlying_asset_id: str
│   └── expiration_date: str
└── relationships:
    ├── HAS_LISTING -> Listing (1:many)
    └── HAS_UNDERLYING_ASSET -> Stock (1:1)

Bond (extends BaseEntity)
└── relationships:
    ├── HAS_LISTING -> Listing (1:many)
    └── HAS_ISSUER -> InstrumentParty (1:1)

Listing (extends BaseEntity)
└── relationships:
    └── HAS_EXCHANGE -> Exchange (1:1)

Exchange (extends BaseEntity)
└── relationships: none (leaf node)

InstrumentParty (extends BaseEntity)
└── relationships:
    └── HAS_ENTITY -> Client (1:1)

Client (extends BaseEntity)
└── relationships: none (leaf node)

TreeListNode (extends BaseEntity)
├── properties:
│   ├── source_entity_id: str
│   ├── relationship_name: str
│   └── target_type: str
└── purpose: placeholder for expensive relationships
```

### 5. Cache Layer
```
CacheInterface (Abstract)
├── get(key) -> Optional[Any]
├── set(key, value, ttl) -> None
├── delete(key) -> None
├── exists(key) -> bool
└── clear() -> None

MemoryCache (implements CacheInterface)
├── uses: CacheEntry
├── properties:
│   ├── _cache: Dict[str, CacheEntry]
│   ├── _lock: threading.RLock
│   └── _stats: Dict[str, int]
├── methods:
│   ├── get_stats() -> Dict[str, int]
│   └── cleanup_expired() -> int
└── thread-safe: Yes

CacheEntry
├── properties:
│   ├── value: Any
│   ├── created_at: datetime
│   └── expires_at: Optional[datetime]
└── methods:
    └── is_expired() -> bool

CacheManager
├── uses: CacheInterface
├── properties:
│   ├── _cache: CacheInterface
│   ├── _enabled: bool
│   └── _default_ttl: int
├── methods:
│   ├── enable() -> None
│   ├── disable() -> None
│   ├── is_enabled() -> bool
│   ├── generate_key(prefix, *args, **kwargs) -> str
│   ├── cached_method(ttl, key_prefix) -> Decorator
│   └── invalidate_pattern(pattern) -> int
└── provides: method caching decorator
```

### 6. Configuration Layer
```
ConfigurationManager
├── properties:
│   ├── config_dir: Path
│   ├── _entity_config: Dict
│   └── _relationship_config: Dict
├── methods:
│   ├── get_generic_entities() -> Dict
│   ├── get_specific_entity_config(entity_type) -> Optional[Dict]
│   ├── get_entity_relationships(entity_type) -> List[Dict]
│   ├── get_relationship_config(source_type, relationship_name) -> Optional[Dict]
│   ├── get_data_provider_config(entity_type) -> Optional[Dict]
│   ├── reload_configurations() -> None
│   └── get_metadata_for_api() -> Dict
└── loads from:
    ├── entity_types.yaml
    └── relationships.yaml
```

## Business Domain Relationships

### Financial Entity Relationships
```
Stock
  ├─[HAS_LISTING]────────→ Listing (1:many)
  │                           │
  │                           └─[HAS_EXCHANGE]──→ Exchange (1:1)
  │
  ├─[HAS_ISSUER]─────────→ InstrumentParty (1:1)
  │                           │
  │                           └─[HAS_ENTITY]────→ Client (1:1)
  │
  └─[IS_UNDERLYING_FOR]──→ Option (1:many, expensive)
                              │
                              └─[HAS_LISTING]──→ Listing (1:many)

Option
  ├─[HAS_UNDERLYING]─────→ Stock (1:1)
  └─[HAS_LISTING]────────→ Listing (1:many)
                              │
                              └─[HAS_EXCHANGE]──→ Exchange (1:1)

Future
  ├─[HAS_UNDERLYING_ASSET]→ Stock (1:1)
  └─[HAS_LISTING]────────→ Listing (1:many)
                              │
                              └─[HAS_EXCHANGE]──→ Exchange (1:1)

Bond
  ├─[HAS_ISSUER]─────────→ InstrumentParty (1:1)
  │                           │
  │                           └─[HAS_ENTITY]────→ Client (1:1)
  └─[HAS_LISTING]────────→ Listing (1:many)
                              │
                              └─[HAS_EXCHANGE]──→ Exchange (1:1)
```

## Data Flow Patterns

### 1. Graph Building Flow
```
User Request (POST /api/graph/build)
  │
  ├→ GraphBuilderHandler
  │   │
  │   └→ GraphService.build_initial_graph()
  │       │
  │       ├→ [Check Cache] CacheManager.get()
  │       │   └→ If cached, return immediately
  │       │
  │       └→ GraphBuilder.build_graph()
  │           │
  │           ├→ ConfigurationManager.resolve_entity_type()
  │           │   └→ DataProvider.resolve_entity_type()
  │           │
  │           ├→ DataProvider.get_entity_by_id()
  │           │   ├→ [Check Cache] CachedProviderMixin
  │           │   └→ BaseEntity instance created
  │           │
  │           ├→ _build_graph_recursive() [2 levels max]
  │           │   │
  │           │   ├→ ConfigurationManager.get_entity_relationships()
  │           │   │
  │           │   ├→ For each relationship:
  │           │   │   │
  │           │   │   ├→ If expensive: create TreeListNode
  │           │   │   │
  │           │   │   └→ Else:
  │           │   │       ├→ DataProvider.get_related_entity_ids()
  │           │   │       │   └→ Returns List[Tuple[id_type, id_value]]
  │           │   │       │
  │           │   │       └→ For each ID:
  │           │   │           ├→ DataProvider.get_entity_by_id()
  │           │   │           └→ Recursive call (depth - 1)
  │           │   │
  │           │   └→ Collect nodes and edges
  │           │
  │           └→ [Cache Result] CacheManager.set()
  │
  └→ Return JSON response {nodes: [], edges: []}
```

### 2. Node Expansion Flow
```
User Click on Node (POST /api/graph/node/expand)
  │
  └→ NodeExpandHandler
      │
      └→ GraphService.expand_node()
          │
          ├→ [Check Cache] CacheManager.get()
          │   └→ If cached, return immediately
          │
          └→ GraphBuilder.expand_node()
              │
              ├→ DataProvider.get_entity_by_id(parent_node)
              │   └→ Parent context passed for optimization
              │
              ├→ _build_graph_recursive() [1 level only]
              │   └→ Build immediate relationships
              │
              └→ [Cache Result] CacheManager.set()
```

### 3. Entity Creation with Parent Context
```
get_entity_by_id(entity_type, id_type, id_value, parent_node)
  │
  ├→ [Validate] Use parent_node for validation if provided
  │   └→ Example: Verify Option belongs to parent Stock
  │
  ├→ [Optimize] Use parent data to filter/optimize query
  │
  ├→ _get_<entity>_data(id_value)
  │   └→ Fetch from mock_data/*.json
  │
  └→ create_entity_instance(entity_type, data)
      └→ Factory creates appropriate entity class
          └→ Returns: Stock|Option|Future|Bond|Listing|Exchange|...
```

### 4. Relationship Resolution with ID Tuples
```
get_related_entity_ids(source_entity, relationship_name)
  │
  ├→ Determine relationship type
  │   └→ Example: Stock.HAS_LISTING
  │
  ├→ Query related entities
  │   └→ Returns: [("tradingLineId", "TL-100"), ("tradingLineId", "TL-101")]
  │
  └→ Advantages:
      ├→ Memory efficient (only IDs, not full objects)
      ├→ Lazy loading (entities loaded on demand)
      └→ Supports different ID types per relationship
```

## Caching Strategy

### Cache Levels
```
Level 1: Entity Cache
  ├→ Key: "entity:{entity_type}:{id_type}:{id_value_hash}"
  ├→ TTL: Variable by entity type (3-60 minutes)
  └→ Stores: BaseEntity instances

Level 2: Relationship Cache
  ├→ Key: "relationship:{name}:{source_type}:{source_id}"
  ├→ TTL: Variable by relationship (3-30 minutes)
  └→ Stores: List[Tuple[id_type, id_value]]

Level 3: Graph Cache
  ├→ Key: "graph_build:{ref_type}:{id_type}:{id_value_hash}"
  ├→ TTL: 5 minutes
  └→ Stores: Complete graph response {nodes, edges}

Level 4: Metadata Cache
  ├→ Key: "meta:{config_type}"
  ├→ TTL: 60 minutes
  └→ Stores: Configuration metadata
```

## Extension Points

### Adding a New Entity Type

1. **Create Entity Class** (entities/entity_types.py)
```python
class NewEntity(BaseEntity):
    def _get_primary_id(self) -> str:
        return self.data.get('newEntityId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        # Implementation
    
    @property
    def custom_property(self) -> str:
        return self.data.get('customField', '')
```

2. **Update Configuration** (config/entity_types.yaml)
```yaml
specific_entities:
  NewEntity:
    parent_type: "ParentType"
    display_config: {...}
    data_source:
      provider: "NewDataProvider"
      method: "get_new_entity_by_id"
```

3. **Define Relationships** (config/relationships.yaml)
```yaml
relationships:
  NewEntity:
    - name: "HAS_RELATED"
      target_type: "RelatedEntity"
      cardinality: "1:many"
      expensive: false
```

4. **Update Data Provider**
```python
def get_entity_by_id(self, entity_type, ...):
    if entity_type == "NewEntity":
        data = self._get_new_entity_data(id_value)
        return self.create_entity_instance('NewEntity', data)
```

5. **Update Factory** (base_provider.py)
```python
entity_classes = {
    ...
    'NewEntity': NewEntity
}
```

### Adding a New Relationship

1. **Update Configuration** (relationships.yaml)
```yaml
SourceEntity:
  - name: "NEW_RELATIONSHIP"
    target_type: "TargetEntity"
    cardinality: "1:many"
    expensive: false
```

2. **Implement in Data Provider**
```python
def get_related_entity_ids(self, source_entity, relationship_name):
    if relationship_name == "NEW_RELATIONSHIP":
        return self._get_new_related_ids(source_entity.id)
```

This diagram provides a comprehensive view of all classes, their relationships, dependencies, and data flows in the Financial Data Relationship Explorer system.
