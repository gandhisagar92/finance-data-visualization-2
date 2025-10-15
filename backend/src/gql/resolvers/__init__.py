"""
GraphQL resolvers package.
"""

from .query_resolver import Query
from .tree_resolver import TreeQuery

__all__ = ['Query', 'TreeQuery']
