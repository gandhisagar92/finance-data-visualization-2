specific_entity_definition = {
    "Stock": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "Stock",
            "idType": "${idType}",
            "idValue": {"instrumentId": "${instrumentId}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {
                "additionalLines": {
                    "Instrument Id": "${instrumentId}",
                    "ISIN": "${isin}",
                    "Sector": "${sector}",
                }
            },
            "list-row": {
                "columns": [
                    {
                        "key": "instrumentId",
                        "label": "Instrument ID",
                        "value": "${instrumentId}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "isin",
                        "label": "ISIN",
                        "value": "${isin}",
                        "sortable": False,
                        "filterable": True,
                    },
                ]
            },
        },
    },
    "Option": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "Option",
            "idType": "${idType}",
            "idValue": {"instrumentId": "${instrumentId}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {
                "additionalLines": {
                    "Instrument Id": "${instrumentId}",
                    "ISIN": "${isin}",
                    "OCC Symbol": "${occSymbol}",
                }
            },
            "list-row": {
                "columns": [
                    {
                        "key": "instrumentId",
                        "label": "Instrument ID",
                        "value": "${instrumentId}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "isin",
                        "label": "ISIN",
                        "value": "${isin}",
                        "sortable": False,
                        "filterable": True,
                    },
                ]
            },
        },
    },
    "Listing": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "Listing",
            "idType": "${idType}",
            "idValue": {"tradingLineId": "${tradingLineId}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {
                "additionalLines": {
                    "Trading Line Id": "${tradingLineId}",
                    "RIC": "${ric}",
                    "Sedol": "${sedol}",
                }
            },
            "list-row": {
                "columns": [
                    {
                        "key": "tradingLineId",
                        "label": "Trading Line ID",
                        "value": "${tradingLineId}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "ric",
                        "label": "RIC",
                        "value": "${ric}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "currency",
                        "label": "Currency",
                        "value": "${currency}",
                        "sortable": False,
                        "filterable": True,
                    },
                ]
            },
        },
    },
    "Exchange": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "Exchange",
            "idType": "${idType}",
            "idValue": {"exchangeId": "${exchangeId}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {"additionalLines": {"MIC": "${mic}"}},
            "list-row": {
                "columns": [
                    {
                        "key": "mic",
                        "label": "MIC",
                        "value": "${mic}",
                        "sortable": False,
                        "filterable": True,
                    }
                ]
            },
        },
    },
    "Client": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "Client",
            "idType": "${idType}",
            "idValue": {"eci": "${eci}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {
                "additionalLines": {
                    "ECI": "${eci}",
                    "SPN": "${spn}",
                    "Entity Id": "${entityId}",
                }
            },
            "list-row": {
                "columns": [
                    {
                        "key": "eci",
                        "label": "ECI",
                        "value": "${eci}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "spn",
                        "label": "SPN",
                        "value": "${spn}",
                        "sortable": False,
                        "filterable": True,
                    },
                ]
            },
        },
    },
    "InstrumentParty": {
        "header": {
            "id": "${id}",
            "titleLine1": "${titleLine1}",
            "titleLine2": "${titleLine2}",
            "status": "${status}",
        },
        "footer": {
            "refDataType": "InstrumentParty",
            "idType": "${idType}",
            "idValue": {"entityId": "${entityId}"},
            "asOf": "${effectiveDate}",
            "source": "${source}",
            "expandable": "${isFurtherExpandable}",
            "payload": "${payload}",
        },
        "body": {
            "graph-node": {
                "additionalLines": {
                    "ECI": "${eci}",
                    "SPN": "${spn}",
                    "Entity Id": "${entityId}",
                }
            },
            "list-row": {
                "columns": [
                    {
                        "key": "eci",
                        "label": "ECI",
                        "value": "${eci}",
                        "sortable": False,
                        "filterable": True,
                    },
                    {
                        "key": "spn",
                        "label": "SPN",
                        "value": "${spn}",
                        "sortable": False,
                        "filterable": True,
                    },
                ]
            },
        },
    },
}
