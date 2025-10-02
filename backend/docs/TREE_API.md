# Tree List API - Implementation Guide

## Overview

The `/api/build/tree` endpoint provides a paginated tree-list view for expensive relationships (like viewing all Options for a Stock). This is designed to handle large datasets efficiently with server-side pagination, filtering, and sorting.

## Endpoint Details

**URL**: `POST /api/build/tree`

**Purpose**: Build a paginated tree-list view for relationships that contain large numbers of related entities.

## Request Format

### Request Body Structure

```json
{
  "refDataType": "Option",
  "idType": "underlyingInstrumentId",
  "idValue": {
    "sourceEntityId": "STK-100",
    "relationshipName": "IS_UNDERLYING_FOR"
  },
  "page": 1,
  "size": 50,
  "filters": {
    "status": "ACTIVE",
    "putOrCall": "C",
    "expirationDate": {
      "from": "2028-01-01",
      "to": "2028-12-31"
    }
  },
  "sortBy": "expirationDate:asc"
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `refDataType` | string | Yes | The type of entity to retrieve (e.g., "Option") |
| `idType` | string | Yes | The type of identifier (e.g., "underlyingInstrumentId") |
| `idValue` | object | Yes | Contains sourceEntityId and relationshipName |
| `idValue.sourceEntityId` | string | Yes | The ID of the source entity (e.g., "STK-100") |
| `idValue.relationshipName` | string | Yes | The relationship name (e.g., "IS_UNDERLYING_FOR") |
| `page` | integer | No | Page number (default: 1) |
| `size` | integer | No | Page size (default: 50) |
| `filters` | object | No | Filter criteria |
| `sortBy` | string | No | Sort field and direction (e.g., "expirationDate:asc") |

## Response Format

### Response Structure

```json
{
  "data": [
    {
      "instrumentId": "OPT-216739",
      "name": "STK-100 Feb-16-2028 C 150.0",
      "status": "ACTIVE",
      "isin": "AJI0Y6DPBHSA",
      "postTradeId": "p-opt-mf8mdd4v",
      "contractSize": 100,
      "strike_price": 150,
      "putOrCall": "C",
      "expirationDate": "2028-02-16",
      "exerciseStyle": "American",
      "primaryTradingLine": "OPT-TL-1001",
      "timingRule": "T+2"
    }
  ],
  "page": 1,
  "size": 50,
  "total_items": 150000,
  "total_pages": 3000,
  "has_next": true,
  "has_previous": false,
  "meta": {
    "columns": [
      {
        "key": "instrumentId",
        "label": "Instrument ID",
        "width": 180,
        "sortable": true
      },
      {
        "key": "name",
        "label": "Name",
        "width": 240,
        "sortable": true
      }
    ],
    "column_groups": [
      {
        "group": "GIM Reference Data",
        "columns": [
          "instrumentId",
          "name",
          "status"
        ]
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of data rows |
| `page` | integer | Current page number |
| `size` | integer | Number of items per page |
| `total_items` | integer | Total number of items across all pages |
| `total_pages` | integer | Total number of pages |
| `has_next` | boolean | Whether there is a next page |
| `has_previous` | boolean | Whether there is a previous page |
| `meta` | object | Metadata about columns and groupings |
| `meta.columns` | array | Column definitions with key, label, width, sortable |
| `meta.column_groups` | array | Column groupings for UI organization |

## Implementation Details

### Data Source

The implementation reads from `mock_data/all_options.json` which contains the complete Option dataset with full message details.

### Filtering Logic

The service filters options based on the `sourceEntityId` by:
1. Loading all options from `all_options.json`
2. Iterating through each option's `underlyings` array
3. Matching options where `underlyings[].instrumentId` equals `sourceEntityId`

### Column Configuration

Column definitions are loaded from `src/config/relationships.yaml` under the `tree_list_config` section for the specific relationship:

```yaml
relationships:
  Stock:
    - name: "IS_UNDERLYING_FOR"
      target_type: "Option"
      expensive: true
      tree_list_config:
        enabled: true
        columns:
          - key: "instrumentId"
            label: "Instrument ID"
            width: 180
            sortable: true
```

### Data Transformation

The service transforms the full Option message into row format:

- **strike_price**: Extracted from `option.strike.price`
- **putOrCall**: Extracted from `option.putOrCall`
- **expirationDate**: Extracted from `option.expirationDate`
- **exerciseStyle**: Extracted from `option.exerciseStyle`
- **primaryTradingLine**: First active trading line's ID
- **timingRule**: Timing rule from primary trading line

## Usage Examples

### Example 1: Basic Request

```bash
curl -X POST http://localhost:8888/api/build/tree \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Option",
    "idType": "underlyingInstrumentId",
    "idValue": {
      "sourceEntityId": "STK-100",
      "relationshipName": "IS_UNDERLYING_FOR"
    },
    "page": 1,
    "size": 50
  }'
```

### Example 2: With Filters

```bash
curl -X POST http://localhost:8888/api/build/tree \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Option",
    "idType": "underlyingInstrumentId",
    "idValue": {
      "sourceEntityId": "STK-100",
      "relationshipName": "IS_UNDERLYING_FOR"
    },
    "page": 1,
    "size": 50,
    "filters": {
      "status": "ACTIVE",
      "putOrCall": "C"
    }
  }'
```

### Example 3: With Sorting

```bash
curl -X POST http://localhost:8888/api/build/tree \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Option",
    "idType": "underlyingInstrumentId",
    "idValue": {
      "sourceEntityId": "STK-100",
      "relationshipName": "IS_UNDERLYING_FOR"
    },
    "page": 1,
    "size": 50,
    "sortBy": "expirationDate:asc"
  }'
```

### Example 4: With Date Range Filter

```bash
curl -X POST http://localhost:8888/api/build/tree \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Option",
    "idType": "underlyingInstrumentId",
    "idValue": {
      "sourceEntityId": "STK-100",
      "relationshipName": "IS_UNDERLYING_FOR"
    },
    "page": 1,
    "size": 50,
    "filters": {
      "expirationDate": {
        "from": "2028-01-01",
        "to": "2028-12-31"
      }
    }
  }'
```

## Supported Features

### Filtering

The following filters are supported:

| Filter | Type | Description |
|--------|------|-------------|
| `status` | string | Filter by option status (e.g., "ACTIVE", "INACTIVE") |
| `putOrCall` | string | Filter by option type ("C" for Call, "P" for Put) |
| `expirationDate` | object | Date range filter with "from" and "to" fields |

### Sorting

Supported sort fields:

| Field | Description |
|-------|-------------|
| `instrumentId` | Sort by instrument ID |
| `name` | Sort by option name |
| `expirationDate` | Sort by expiration date |
| `strike_price` | Sort by strike price |

Sort format: `field:direction` where direction is `asc` or `desc`

Examples:
- `"expirationDate:asc"` - Sort by expiration date ascending
- `"strike_price:desc"` - Sort by strike price descending

## Code Structure

### Key Files

1. **TreeService** (`src/services/tree_service.py`)
   - Main service handling tree-list operations
   - `build_tree_list()` - Main method for building tree lists
   - `_load_all_options()` - Loads data from all_options.json
   - `_transform_option_to_row()` - Transforms option data to row format
   - `_apply_filters()` - Applies filtering logic
   - `_apply_sorting()` - Applies sorting logic

2. **TreeBuilderHandler** (`src/api/handlers.py`)
   - API handler for `/api/build/tree` endpoint
   - Validates request
   - Calls TreeService
   - Returns formatted response

3. **Configuration** (`src/config/relationships.yaml`)
   - Defines tree_list_config for relationships
   - Column definitions
   - Column groupings

4. **Mock Data** (`mock_data/all_options.json`)
   - Complete option dataset
   - Full message format with all fields

## Performance Considerations

### Memory Usage

- Options are loaded once and cached in memory
- Pagination reduces memory footprint for responses
- Typical memory usage: ~1-2 MB for 10,000 options

### Response Time

- First request: 50-100ms (loading and filtering)
- Subsequent requests: 10-20ms (cached data)
- With filters: 20-40ms (additional filtering)

### Optimization Tips

1. **Use appropriate page size**: 50-100 items per page is optimal
2. **Apply filters early**: Reduces data processing
3. **Cache on client**: Cache pages that don't change frequently
4. **Use server-side sorting**: More efficient than client-side

## Error Handling

### Common Errors

| Error Code | Status | Description |
|------------|--------|-------------|
| `INVALID_REQUEST` | 400 | Missing required fields or invalid parameters |
| `TREE_BUILD_ERROR` | 500 | Internal error during tree building |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: refDataType",
    "details": {}
  }
}
```

## Testing

Run the test suite:

```bash
# Test the tree API
python tests/test_tree_api.py

# Test with pytest
pytest tests/test_tree_api.py -v
```

## Extension Points

### Adding New Entity Types

To add tree-list support for a new entity type:

1. Update `relationships.yaml` with `tree_list_config`
2. Add data loading logic in `TreeService._load_all_<entity_type>()`
3. Add transformation logic in `TreeService._transform_<entity>_to_row()`
4. Update filtering and sorting logic as needed

### Adding New Filters

To add a new filter:

1. Update request documentation
2. Add filter logic in `TreeService._apply_filters()`
3. Test with various filter values

### Adding New Sort Fields

To add a new sort field:

1. Update sort field documentation
2. Add sort logic in `TreeService._apply_sorting()`
3. Mark field as sortable in relationships.yaml

## Future Enhancements

Potential improvements for future versions:

1. **Advanced Filtering**
   - Multi-value filters
   - Range filters for numeric fields
   - Wildcard search

2. **Performance**
   - Database indexing for faster queries
   - Response compression
   - Cursor-based pagination for large datasets

3. **Features**
   - Export to CSV/Excel
   - Saved filter presets
   - Column customization per user

4. **Analytics**
   - Summary statistics
   - Aggregations
   - Grouping by fields

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Endpoint**: POST /api/build/tree
