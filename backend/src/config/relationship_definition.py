relationship_definition = {
    "Stock": [
        {
            "name": "HAS_LISTING",
            "targetType": "Listing",
            "cardinality": "1:n",
            "label": "LISTING",
            "expensive": False,
        },
        {
            "name": "HAS_ISSUER",
            "targetType": "InstrumentParty",
            "cardinality": "1:1",
            "label": "ISSUER",
            "expensive": False,
        },
        {
            "name": "IS_UNDERLYING_FOR",
            "targetType": "Option",
            "cardinality": "1:n",
            "label": "HAS_OPTIONS",
            "expensive": True,
        },
    ],
    "Listing": [
        {
            "name": "LISTED_ON",
            "targetType": "Exchange",
            "cardinality": "1:1",
            "label": "EXCHANGE",
            "expensive": False,
        }
    ],
    "Option": [
        {
            "name": "HAS_LISTING",
            "targetType": "Listing",
            "cardinality": "1:n",
            "label": "LISTING",
            "expensive": False,
        }
    ],
    "InstrumentParty": [
        {
            "name": "PARTY_OF",
            "targetType": "Client",
            "cardinality": "1:1",
            "label": "PARTY",
            "expensive": False,
        }
    ],
}
