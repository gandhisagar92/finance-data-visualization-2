# Quick Start Guide

## Get Started in 3 Minutes

### 1. Install Dependencies (30 seconds)
```bash
pip install -r requirements.txt
```

### 2. Run Tests (30 seconds)
```bash
python test_setup.py
```

Expected output:
```
============================================================
Financial Data Explorer - Component Tests
============================================================

Testing Configuration Manager...
✓ Loaded 3 reference data types
✓ Stock entity definition loaded
✓ Stock has 3 relationships
Configuration Manager: PASSED

Testing Data Providers...
✓ Stock provider initialized
✓ Fetched stock: Company 1
✓ Listing provider initialized
✓ Exchange provider initialized
Data Providers: PASSED

Testing Graph Builder...
✓ Built graph with X nodes and Y edges
  Node 1: Common Stock - Company 1
  Node 2: Trading Line - 
  Node 3: XMAD - Madrid Exchange GBP
Graph Builder: PASSED

Testing Entity Transformation...
✓ Transformed entity to node:
  ID: STK-100
  Title: Common Stock - Company 1
  Status: ACTIVE
Entity Transformation: PASSED

============================================================
ALL TESTS PASSED!
============================================================

You can now start the server with: python main.py
```

### 3. Start Server (10 seconds)
```bash
python main.py
```

Expected output:
```
Starting Financial Data Relationship Explorer on port 8888...
API endpoints:
  - GET  http://localhost:8888/api/meta
  - POST http://localhost:8888/api/graph/build
  - POST http://localhost:8888/api/graph/node/expand
  - GET  http://localhost:8888/api/graph/node/payload
  - POST http://localhost:8888/api/tree/build
  - POST http://localhost:8888/api/tree/item/expand
  - GET  http://localhost:8888/api/type/resolve

Press Ctrl+C to stop the server
```

## Try Your First API Call

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

You should see a JSON response with nodes and edges!

## What You Can Query

### Available Stocks
- STK-100, STK-102, STK-103, STK-104, STK-105, STK-106, STK-107, STK-108, STK-109, STK-110
- STK-111, STK-112, STK-113, STK-114, STK-115, STK-116, STK-117, STK-118, STK-119, STK-120

### Example Queries

**Query by Instrument ID:**
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{"refDataType": "Stock", "idType": "instrumentId", "idValue": {"instrumentId": "STK-100"}}'
```

**Query by ISIN:**
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{"refDataType": "Stock", "idType": "isin", "idValue": {"isin": "E4KLWPQSUPV2"}}'
```

**Query Trading Line:**
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{"refDataType": "Listing", "idType": "tradingLineId", "idValue": {"tradingLineId": "TL-1001"}}'
```

**Query Exchange:**
```bash
curl -X POST http://localhost:8888/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{"refDataType": "Exchange", "idType": "exchangeId", "idValue": {"exchangeId": "XMAD"}}'
```

## Understanding the Response

### Node Structure
```json
{
  "id": "STK-100",
  "titleLine1": "Common Stock",
  "titleLine2": "Company 1",
  "status": "ACTIVE",
  "additionalLines": {
    "Instrument Id": "STK-100",
    "ISIN": "E4KLWPQSUPV2",
    "Sector": "Equity"
  },
  "refDataType": "Stock",
  "idType": "instrumentId",
  "idValue": {"instrumentId": "STK-100"},
  "asOf": "2025-09-15T10:47:10",
  "expandable": true
}
```

### Edge Structure
```json
{
  "source": "STK-100",
  "target": "TL-1001",
  "relationship": "LISTING"
}
```

## Exploring Relationships

The graph will show:
- **Stock** → Listings (Trading Lines)
- **Listing** → Exchange
- **Stock** → Issuer (Instrument Party)
- **Instrument Party** → Client (Party)
- **Stock** → Options (placeholder for expensive relationship)

## Common Issues

### "Connection refused"
Make sure the server is running: `python main.py`

### "Module not found"
Install dependencies: `pip install -r requirements.txt`

### "Empty graph returned"
Check if the entity ID exists in mock_data/*.json files

### Test failures
Make sure you're running from the project root directory

## Next Steps

1. **Read the README.md** - Full project overview
2. **Check DEVELOPER_GUIDE.md** - Development reference
3. **Review PROJECT_SUMMARY.md** - Architecture details
4. **Explore the code** - Start with `main.py` and follow the flow

## Project Structure Quick Reference

```
Key Files:
- main.py                          → Start here
- test_setup.py                    → Run tests
- src/services/graph_builder.py    → Core graph logic
- src/data_providers/              → Data access
- src/config/entity_definition.py  → Display templates
- mock_data/*.json                 → Data files
```

## Tips

- Use a JSON formatter browser extension for better API response viewing
- Check the terminal for server logs
- Modify mock_data/*.json to test with your own data
- Read the code comments for detailed explanations

## Getting Help

If you encounter issues:
1. Check the error message in terminal
2. Review DEVELOPER_GUIDE.md troubleshooting section
3. Verify your API request format matches the examples
4. Make sure all dependencies are installed

## Success!

If you've made it this far and the tests pass, congratulations! 🎉

You have a fully functional Financial Data Relationship Explorer running locally.

Now you can:
- ✅ Query different entities
- ✅ Build relationship graphs
- ✅ Expand nodes dynamically
- ✅ Explore the codebase
- ✅ Extend with new entity types

Happy exploring! 🚀
