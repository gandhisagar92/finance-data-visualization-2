#!/usr/bin/env python3
"""
Test script to validate GraphQL endpoint functionality
"""

import requests
import json
import sys


def test_graphql_endpoint():
    """Test the GraphQL endpoint with various queries"""

    base_url = "http://localhost:8888"
    graphql_url = f"{base_url}/graphql"

    print("Testing GraphQL endpoint...")
    print(f"URL: {graphql_url}")
    print()

    # Test 1: Schema introspection
    print("1. Testing schema introspection...")
    query1 = {
        "query": """
        query {
          __schema {
            queryType {
              name
            }
          }
        }
        """
    }

    try:
        response = requests.post(graphql_url, json=query1, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Test 2: Query available types
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
        response = requests.post(graphql_url, json=query2, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                fields = data["data"]["__schema"]["queryType"]["fields"]
                print(f"   Available query fields:")
                for field in fields:
                    print(
                        f"     - {field['name']}: {field.get('description', 'No description')}"
                    )
            else:
                print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Test 3: Test getMetadata query
    print("3. Testing getMetadata query...")
    query3 = {
        "query": """
        query {
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
                }
              }
            }
          }
        }
        """
    }

    try:
        response = requests.post(graphql_url, json=query3, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"] and data["data"]["getMetadata"]:
                ref_types = data["data"]["getMetadata"]["referenceDataTypes"]
                print(f"   Found {len(ref_types)} reference data types:")
                for ref_type in ref_types[:3]:  # Show first 3
                    print(
                        f"     - {ref_type['refDataType']}: {ref_type.get('description', 'No description')}"
                    )
                if len(ref_types) > 3:
                    print(f"     ... and {len(ref_types) - 3} more")
            else:
                print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    test_graphql_endpoint()
