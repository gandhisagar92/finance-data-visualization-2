#!/usr/bin/env python3
"""
Fetch metadata using GraphQL query
"""

import urllib.request
import urllib.parse
import json


def fetch_metadata():
    """Fetch metadata from GraphQL endpoint"""

    url = "http://localhost:8888/graphql"

    # GraphQL query for metadata
    query = """
    query GetMetadata {
      getMetadata {
        referenceDataTypes {
          refDataType
          description
          idTypes {
            type
            inputs {
              id
              label
              kind
              required
              options
              validation
            }
          }
        }
      }
    }
    """

    # Create the request payload
    payload = {"query": query}

    try:
        # Convert to JSON and encode
        data = json.dumps(payload).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode("utf-8")
            result = json.loads(response_data)

            print("GraphQL Metadata Query Result:")
            print("=" * 50)
            print(json.dumps(result, indent=2))

            # Pretty print the reference data types
            if "data" in result and result["data"] and "getMetadata" in result["data"]:
                metadata = result["data"]["getMetadata"]
                ref_types = metadata.get("referenceDataTypes", [])

                print(f"\n\nSummary: Found {len(ref_types)} Reference Data Types:")
                print("-" * 50)

                for ref_type in ref_types:
                    print(f"\n📋 {ref_type['refDataType']}")
                    if ref_type.get("description"):
                        print(f"   Description: {ref_type['description']}")

                    id_types = ref_type.get("idTypes", [])
                    print(f"   ID Types: {len(id_types)}")

                    for id_type in id_types:
                        print(f"     • {id_type['type']}")
                        inputs = id_type.get("inputs", [])
                        for input_field in inputs:
                            required = (
                                "Required"
                                if input_field.get("required")
                                else "Optional"
                            )
                            print(
                                f"       - {input_field['label']} ({input_field['kind']}) [{required}]"
                            )

    except Exception as e:
        print(f"Error fetching metadata: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    fetch_metadata()
