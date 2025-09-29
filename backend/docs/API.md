# API Documentation

## Base URL
```
http://localhost:8888
```

## Endpoints

### 1. GET /api/meta
Get metadata for all reference data types and their queryable fields.

**Response:**
```json
{
  "referenceDataTypes": [
    {
      "refDataType": "Instrument",
      "idTypes": [
        {
          "type": "InstrumentId",
          "inputs": [
            {"id": "instrumentId", "label": "Instrument ID", "kind": "text"}
          ]
        },
        {
          "type": "Economics",
          "inputs": [
            {"id": "underlyingInstrumentId", "label": "Underlying Instrument ID", "kind": "text"},
            {"id": "strike", "label": "Strike", "kind": "number"},
            {"id": "callOrPut", "label": "Call or Put", "kind": "select", "options": ["Call", "Put"]}
          ]
        }
      ]
    }
  ]
}
```

### 2. POST /api/graph/build
Build initial relationship graph (2 levels deep).

**Request Body:**
```json
{
  "refDataType": "Instrument",
  "idType": "InstrumentId",
  "idValue": {"instrumentId": "A125989590"},
  "source": "Athena",
  "effectiveDatetime": "2024-01-15 00:00:00"
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "A125989590",
      "titleLine1": "Common Stock",
      "titleLine2": "APPLE INC",
      "status": "ACTIVE",
      "additionalLines": {"Instrument Id": "A125989590", "ISIN": "US0378331005"},
      "refDataType": "Stock",
      "idType": "instrumentId",
      "idValue": {"instrumentId": "A125989590"},
      "asOf": "2025-09-24T12:00:00"
    }
  ],
  "edges": [
    {
      "source": "A125989590",
      "target": "A908908404",
      "relationship": "LISTING"
    }
  ]
}
```

## Testing the API

You can test the API using curl:

```bash
# Get metadata
curl http://localhost:8888/api/meta

# Build a graph for APPLE stock
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "refDataType": "Instrument",
    "idType": "InstrumentId", 
    "idValue": {"instrumentId": "A125989590"}
  }'

# Get node payload
curl "http://localhost:8888/api/graph/node/payload?nodeId=A125989590&refDataType=Stock&idType=instrumentId&idValue=%7B%22instrumentId%22%3A%22A125989590%22%7D"
```
