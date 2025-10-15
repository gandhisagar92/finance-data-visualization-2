#!/usr/bin/env python3
"""
Simple test script to validate GraphQL endpoint using urllib (no external deps)
"""

import urllib.request
import urllib.parse
import json
import sys


def test_graphql_endpoint():
    """Test the GraphQL endpoint with basic queries"""

    base_url = "http://localhost:8888"
    graphql_url = f"{base_url}/graphql"

    print("Testing GraphQL endpoint...")
    print(f"URL: {graphql_url}")
    print()

    # Test 1: Schema introspection
    print("1. Testing schema introspection...")
    query1 = {"query": "query { __schema { queryType { name } } }"}

    try:
        # Convert to JSON and encode
        data = json.dumps(query1).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            graphql_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(data)),
            },
            method="POST",
        )

        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode("utf-8")
            response_json = json.loads(response_data)

            print(f"   Status: {response.status}")
            print(f"   Response: {json.dumps(response_json, indent=2)}")

    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Test 2: Available fields
    print("2. Testing available query fields...")
    query2 = {
        "query": """
        query {
          __schema {
            queryType {
              fields {
                name
                description
              }
            }
          }
        }
        """
    }

    try:
        data = json.dumps(query2).encode("utf-8")
        req = urllib.request.Request(
            graphql_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode("utf-8")
            response_json = json.loads(response_data)

            print(f"   Status: {response.status}")
            if "data" in response_json and response_json["data"]:
                fields = response_json["data"]["__schema"]["queryType"]["fields"]
                print(f"   Available query fields:")
                for field in fields:
                    desc = field.get("description") or "No description"
                    print(f"     - {field['name']}: {desc}")
            else:
                print(f"   Response: {json.dumps(response_json, indent=2)}")

    except Exception as e:
        print(f"   Error: {e}")

    print("\nGraphQL endpoint test completed!")


if __name__ == "__main__":
    test_graphql_endpoint()
