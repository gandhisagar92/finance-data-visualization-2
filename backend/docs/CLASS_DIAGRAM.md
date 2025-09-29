# Class Diagram - Detailed View

## Complete Class Structure with Methods and Properties

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            BaseEntity                                   │
│                           <<abstract>>                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ + data: Dict[str, Any]                                                  │
│ + id: str                                                               │
│ + entity_type: str                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(data: Dict[str, Any])                                        │
│ + _get_primary_id(): str {abstract}                                     │
│ + to_node_dict(): Dict[str, Any] {abstract}                             │
│ + get_field_value(field_name: str): Any                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    △
                                    │ inherits
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│       Stock         │  │      Option          │  │      Future         │
├─────────────────────┤  ├──────────────────────┤  ├─────────────────────┤
│ Properties:         │  │ Properties:          │  │ Properties:         │
│ + instrument_id:str │  │ + underlying_inst..  │  │ + underlying_asset..│
│ + name: str         │  │                      │  │ + expiration_date   │
│ + isin: str         │  │                      │  │                     │
├─────────────────────┤  ├──────────────────────┤  ├─────────────────────┤
│ Methods:            │  │ Methods:             │  │ Methods:            │
│ + _get_primary_id() │  │ + _get_primary_id()  │  │ + _get_primary_id() │
│ + to_node_dict()    │  │ + to_node_dict()     │  │ + to_node_dict()    │
└─────────────────────┘  └──────────────────────┘  └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         BaseDataProvider                                │
│                           <<abstract>>                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ + config: Dict[str, Any]                                                │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(config: Dict[str, Any])                                      │
│ + get_entity_by_id(entity_type: str,                                    |
|                    id_type: str,                                        │
│                    id_value: Dict,                                      |
|                    parent_node: Optional[BaseEntity])                   │
│                          : Optional[BaseEntity] {abstract}              │
│ + get_related_entity_ids(source_entity: BaseEntity,                     │
│                          relationship_name: str)                        │
│                          : List[Tuple[str, str]] {abstract}             │
│ + resolve_entity_type(generic_type: str,                                |
|                       id_type: str,                                     │
│                       id_value: Dict)                                   |
|                          : Optional[str] {abstract}                     │
│ + create_entity_instance(entity_type: str, data: Dict): BaseEntity      │
└─────────────────────────────────────────────────────────────────────────┘
                                    △
                                    │ inherits
                    ┌───────────────┴───────────────┐
                    │                               │
┌──────────────────────────────────────┐  ┌─────────────────────────────┐
│    InstrumentDataProvider            │  │  CachedProviderMixin        │
├──────────────────────────────────────┤  │        <<mixin>>            │
│ + mock_data: Dict[str, Any]          │  ├─────────────────────────────┤
├──────────────────────────────────────┤  │ + cache_manager:            │
│ + _load_mock_data(): Dict            │  │   CacheManager              │
│ + get_entity_by_id(...): BaseEntity  │  ├─────────────────────────────┤
│ + _get_stock_data(id): Dict          │  │ + get_cached_entity(...)    │
│ + _get_option_data(id): Dict         │  │ + get_cached_related_ids()  │
│ + _get_future_data(id): Dict         │  │ + _generate_entity_cache_k..│
│ + _get_bond_data(id): Dict           │  │ + _generate_relationship_k..│
│ + get_related_entity_ids(...):       │  │ + _get_entity_cache_ttl()   │
│   List[Tuple[str, str]]              │  │ + _get_relationship_cache_..│
│ + resolve_entity_type(...): str      │  └─────────────────────────────┘
└──────────────────────────────────────┘            │ mixed into
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │  Combined Implementation       │
                    │  (Multiple Inheritance)        │
                    └────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CacheManager                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ - _cache: CacheInterface                                                │
│ - _enabled: bool                                                        │
│ - _default_ttl: int                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(cache_impl: Optional[CacheInterface])                        │
│ + enable(): None                                                        │
│ + disable(): None                                                       │
│ + is_enabled(): bool                                                    │
│ + get(key: str): Optional[Any]                                          │
│ + set(key: str, value: Any, ttl: Optional[int]): None                  │
│ + delete(key: str): None                                                │
│ + clear(): None                                                         │
│ + generate_key(prefix: str, *args, **kwargs): str                      │
│ + cached_method(ttl: int, key_prefix: str): Decorator                  │
│ + invalidate_pattern(pattern: str): int                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ uses
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CacheInterface                                      │
│                       <<interface>>                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ + get(key: str): Optional[Any] {abstract}                              │
│ + set(key: str, value: Any, ttl: Optional[int]): None {abstract}       │
│ + delete(key: str): None {abstract}                                     │
│ + exists(key: str): bool {abstract}                                     │
│ + clear(): None {abstract}                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    △
                                    │ implements
┌─────────────────────────────────────────────────────────────────────────┐
│                         MemoryCache                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ - _cache: Dict[str, CacheEntry]                                         │
│ - _lock: threading.RLock                                                │
│ - _stats: Dict[str, int]                                                │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__()                                                            │
│ + get(key: str): Optional[Any]                                          │
│ + set(key: str, value: Any, ttl: Optional[int]): None                  │
│ + delete(key: str): None                                                │
│ + exists(key: str): bool                                                │
│ + clear(): None                                                         │
│ + get_stats(): Dict[str, int]                                           │
│ + cleanup_expired(): int                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ uses
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CacheEntry                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ + value: Any                                                            │
│ + created_at: datetime                                                  │
│ + expires_at: Optional[datetime]                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(value: Any, ttl: Optional[int])                              │
│ + is_expired(): bool                                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     ConfigurationManager                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ + config_dir: Path                                                      │
│ - _entity_config: Dict[str, Any]                                        │
│ - _relationship_config: Dict[str, Any]                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(config_dir: Optional[str])                                   │
│ - _load_configurations(): None                                          │
│ + get_generic_entities(): Dict[str, Any]                               │
│ + get_specific_entity_config(entity_type: str): Optional[Dict]         │
│ + get_entity_relationships(entity_type: str): List[Dict]               │
│ + get_relationship_config(source_type: str, rel_name: str): Optional[] │
│ + get_data_provider_config(entity_type: str): Optional[Dict]           │
│ + reload_configurations(): None                                         │
│ + get_metadata_for_api(): Dict[str, Any]                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         GraphBuilder                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + config_manager: ConfigurationManager                                  │
│ + data_providers: Dict[str, BaseDataProvider]                          │
│ + max_initial_depth: int = 2                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(config_manager, data_provider_registry)                      │
│ + build_graph(root_entity_type, id_type, id_value, **kwargs): Dict    │
│ + expand_node(node_id, ref_data_type, id_type, id_value): Dict        │
│ - _build_graph_recursive(source_entity, nodes, edges, visited,         │
│                          current_depth, max_depth): None                │
│ - _create_tree_list_node(source_entity, relationship): BaseEntity      │
│ - _get_expensive_relationship_count(source_entity, relationship): int  │
│ - _get_related_entity(target_type, id_type, id_value, parent): Entity  │
│ - _get_data_provider(entity_type: str): BaseDataProvider               │
│ - _resolve_entity_type(generic_type, id_type, id_value): Optional[str] │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ uses
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         GraphService                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + graph_builder: GraphBuilder                                           │
│ + cache_manager: CacheManager                                           │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(graph_builder, cache_manager)                                │
│ + build_initial_graph(ref_data_type, id_type, id_value, **kwargs):Dict│
│ + expand_node(node_id, ref_data_type, id_type, id_value): Dict        │
│ + invalidate_node_cache(entity_type, entity_id): None                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          TreeService                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + data_providers: Dict[str, BaseDataProvider]                          │
│ + config_manager: ConfigurationManager                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(data_provider_registry, config_manager)                      │
│ + build_tree_list(ref_data_type, id_type, id_value, page,             │
│                   page_size, filters, sort_by): Dict                   │
│ + expand_tree_item(node_data): Dict                                    │
│ - _build_paginated_tree(provider, ref_data_type, id_type, id_value,   │
│                         page, page_size, filters, sort_by): Dict       │
│ - _entity_to_columns(entity): Dict[str, Any]                           │
│ - _get_data_provider(entity_type: str): BaseDataProvider               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     DataProviderRegistry                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ - _providers: Dict[str, BaseDataProvider]                              │
│ - _provider_classes: Dict[str, Type[BaseDataProvider]]                 │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__()                                                            │
│ + register_provider(name: str, provider: BaseDataProvider): None       │
│ + get_provider(name: str): BaseDataProvider                            │
│ + initialize_all_providers(config: Dict, cache_manager): None          │
│ + get_all_providers(): Dict[str, BaseDataProvider]                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          BaseHandler                                     │
│                      <<Tornado Handler>>                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ + set_default_headers(): None                                           │
│ + options(): None                                                       │
│ + write_json(data: Dict): None                                         │
│ + write_error_response(error_code, message, status_code, details): None│
│ + get_json_body(): Dict[str, Any]                                      │
│ + validate_required_fields(data: Dict, required_fields: list): None    │
└─────────────────────────────────────────────────────────────────────────┘
                                    △
                                    │ inherits
          ┌────────────┬────────────┼────────────┬────────────┐
          │            │            │            │            │
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌───────────────┐
│MetadataHandler   │ │GraphBuilderHandler│ │NodeExpandHandler │ │TreeBuilder... │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤ ├───────────────┤
│+ config_manager  │ │+ graph_service   │ │+ graph_service   │ │+ tree_service │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤ ├───────────────┤
│+ get(): None     │ │+ post(): None    │ │+ post(): None    │ │+ post(): None │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └───────────────┘
```

## Dependency Graph (Imports)

```
main.py
  ├─► config.config_manager.ConfigurationManager
  ├─► data_providers.registry.DataProviderRegistry
  ├─► cache.cache_manager.CacheManager
  ├─► services.graph_builder.GraphBuilder
  ├─► services.graph_service.GraphService
  ├─► services.tree_service.TreeService
  └─► api.handlers.*

api.handlers
  ├─► api.base_handler.BaseHandler
  ├─► config.config_manager.ConfigurationManager
  ├─► services.graph_service.GraphService
  ├─► services.tree_service.TreeService
  └─► data_providers.base_provider.BaseDataProvider

services.graph_builder
  ├─► entities.entity_types.BaseEntity
  ├─► entities.entity_types.TreeListNode
  ├─► data_providers.base_provider.BaseDataProvider
  └─► config.config_manager.ConfigurationManager

services.graph_service
  ├─► services.graph_builder.GraphBuilder
  └─► cache.cache_manager.CacheManager

services.tree_service
  ├─► data_providers.base_provider.BaseDataProvider
  └─► config.config_manager.ConfigurationManager

data_providers.instrument_provider
  ├─► data_providers.base_provider.BaseDataProvider
  ├─► data_providers.cached_provider_mixin.CachedProviderMixin
  └─► entities.entity_types.BaseEntity

data_providers.cached_provider_mixin
  ├─► cache.cache_manager.CacheManager
  └─► entities.entity_types.BaseEntity

data_providers.base_provider
  └─► entities.entity_types.*

cache.cache_manager
  └─► cache.cache_interface.CacheInterface
  └─► cache.memory_cache.MemoryCache

cache.memory_cache
  └─► cache.cache_interface.CacheInterface
  └─► cache.cache_interface.CacheEntry

config.config_manager
  └─► yaml (external)
```

## Method Call Sequence Diagrams

### Scenario 1: Building Initial Graph

```
User → GraphBuilderHandler.post()
  │
  ├─► validate_required_fields()
  │
  ├─► GraphService.build_initial_graph()
  │     │
  │     ├─► CacheManager.generate_key()
  │     │
  │     ├─► CacheManager.get()  [Check cache]
  │     │     └─► MemoryCache.get()
  │     │
  │     └─► GraphBuilder.build_graph()
  │           │
  │           ├─► _resolve_entity_type()
  │           │     └─► InstrumentDataProvider.resolve_entity_type()
  │           │
  │           ├─► InstrumentDataProvider.get_entity_by_id()
  │           │     ├─► CachedProviderMixin.get_cached_entity()
  │           │     │     ├─► CacheManager.get()
  │           │     │     └─► [if miss] _get_stock_data()
  │           │     └─► create_entity_instance('Stock', data)
  │           │           └─► Stock.__init__(data)
  │           │
  │           └─► _build_graph_recursive()
  │                 │
  │                 ├─► ConfigurationManager.get_entity_relationships()
  │                 │
  │                 ├─► For each relationship:
  │                 │     │
  │                 │     ├─► [if expensive] _create_tree_list_node()
  │                 │     │     └─► TreeListNode.__init__()
  │                 │     │
  │                 │     └─► [else] InstrumentDataProvider.get_related_entity_ids()
  │                 │           │
  │                 │           ├─► _get_instrument_listing_ids()
  │                 │           │     └─► returns [("tradingLineId", "TL-100"), ...]
  │                 │           │
  │                 │           └─► For each ID tuple:
  │                 │                 ├─► _get_related_entity()
  │                 │                 │     └─► ListingDataProvider.get_entity_by_id()
  │                 │                 │           └─► Listing.__init__(data)
  │                 │                 │
  │                 │                 └─► _build_graph_recursive() [recursive, depth-1]
  │                 │
  │                 └─► collect nodes and edges
  │
  └─► CacheManager.set()  [Cache result]
        └─► MemoryCache.set()
              └─► CacheEntry.__init__(value, ttl)
```

### Scenario 2: Entity Creation with Parent Context

```
GraphBuilder._get_related_entity()
  │
  └─► ListingDataProvider.get_entity_by_id(
        entity_type="Listing",
        id_type="tradingLineId",
        id_value={"tradingLineId": "TL-100"},
        parent_node=<Stock instance>  ← Parent context passed
      )
        │
        ├─► [Validate] Check if parent_node is relevant
        │     └─► if parent_node.entity_type == "Stock":
        │           # Can use parent data for validation
        │
        ├─► _get_listing_data("TL-100")
        │     └─► Load from mock_data/listings.json
        │
        └─► create_entity_instance("Listing", data)
              └─► Listing.__init__(data)
                    ├─► BaseEntity.__init__(data)
                    │     ├─► self.data = data
                    │     ├─► self.id = _get_primary_id()
                    │     └─► self.entity_type = "Listing"
                    │
                    └─► return Listing instance
```

### Scenario 3: Caching Flow

```
CachedProviderMixin.get_cached_entity()
  │
  ├─► _generate_entity_cache_key(entity_type, id_type, id_value)
  │     └─► CacheManager.generate_key()
  │           └─► returns "entity:Stock:instrumentId:hash123"
  │
  ├─► CacheManager.get("entity:Stock:instrumentId:hash123")
  │     │
  │     └─► MemoryCache.get("entity:Stock:instrumentId:hash123")
  │           │
  │           ├─► Check if key exists in _cache
  │           │
  │           ├─► Check if CacheEntry.is_expired()
  │           │     └─► datetime.now() > expires_at?
  │           │
  │           └─► [if valid] return entry.value
  │                        └─► return <Stock instance>
  │
  ├─► [if cache miss] get_entity_by_id(...)
  │     └─► Fetch from data source
  │
  ├─► _get_entity_cache_ttl("Stock")
  │     └─► returns 300  # 5 minutes
  │
  └─► CacheManager.set(cache_key, entity, 300)
        └─► MemoryCache.set(cache_key, entity, 300)
              └─► CacheEntry(entity, ttl=300)
                    ├─► self.value = entity
                    ├─► self.created_at = datetime.now()
                    └─► self.expires_at = created_at + timedelta(seconds=300)
```

This comprehensive class diagram shows all the classes, their methods, properties, relationships, and the detailed interaction flows throughout the application.
