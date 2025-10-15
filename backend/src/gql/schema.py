"""
GraphQL Schema definition.
Combines all types and resolvers into a single schema.
"""

import graphene
from src.gql.resolvers.query_resolver import Query
from src.gql.resolvers.tree_resolver import TreeQuery


# Combine all query fields into a single Query type
class RootQuery(Query, TreeQuery, graphene.ObjectType):
    """Combined root query type"""

    pass


# Create the GraphQL schema
def create_schema():
    """Create and return the GraphQL schema"""
    return graphene.Schema(
        query=RootQuery,
        # mutation=Mutation,  # Add when mutations are needed
        # subscription=Subscription,  # Add for real-time features
    )
