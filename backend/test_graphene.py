#!/usr/bin/env python3
"""
Test script to check Graphene imports and basic functionality
"""

import sys
import os

# Add src to path like in main_graphql.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("Testing Graphene imports...")

try:
    import graphene

    print("✓ graphene imported successfully")
    print(f"  Version: {graphene.__version__}")

    # Test basic types
    print("Testing basic Graphene types...")

    class TestEnum(graphene.Enum):
        VALUE1 = "VALUE1"
        VALUE2 = "VALUE2"

    print("✓ graphene.Enum works")

    class TestType(graphene.ObjectType):
        name = graphene.String()

    print("✓ graphene.ObjectType works")

    class TestInput(graphene.InputObjectType):
        name = graphene.String()

    print("✓ graphene.InputObjectType works")

    print("All basic Graphene functionality works!")

except Exception as e:
    print(f"✗ Error testing Graphene: {e}")
    import traceback

    traceback.print_exc()

print("\nTesting our GraphQL types...")

try:
    from src.gql.types.graph_types import NodeStatus, GraphNode

    print("✓ Our graph types imported successfully")

except Exception as e:
    print(f"✗ Error importing our types: {e}")
    import traceback

    traceback.print_exc()

print("\nTesting GraphQL schema...")

try:
    from src.gql.schema import create_schema

    schema = create_schema()
    print("✓ Schema created successfully")
    print(f"  Schema type: {type(schema)}")

except Exception as e:
    print(f"✗ Error creating schema: {e}")
    import traceback

    traceback.print_exc()

print("\nTest completed!")
