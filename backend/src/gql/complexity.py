"""
Query complexity analyzer and validator.
Prevents expensive queries from overwhelming the server.
"""

from graphql import GraphQLError
from graphql.language import ast
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class QueryComplexityValidator:
    """
    Validates GraphQL query complexity to prevent resource exhaustion.
    
    Complexity is calculated based on:
    - Field selections (each field adds cost)
    - Nested depth (deeper queries cost more)
    - List fields (can return many items)
    - Expensive operations (marked fields)
    """
    
    def __init__(
        self,
        max_complexity: int = 1000,
        max_depth: int = 10,
        default_field_cost: int = 1,
        expensive_field_cost: int = 50
    ):
        """
        Initialize complexity validator.
        
        Args:
            max_complexity: Maximum total complexity score allowed
            max_depth: Maximum nesting depth allowed
            default_field_cost: Cost for regular fields
            expensive_field_cost: Cost for expensive operations
        """
        self.max_complexity = max_complexity
        self.max_depth = max_depth
        self.default_field_cost = default_field_cost
        self.expensive_field_cost = expensive_field_cost
        
        # Define expensive operations
        self.expensive_fields = {
            "buildGraph": 100,      # Building graph is expensive
            "expandNode": 50,       # Expanding node is moderate
            "buildTreeList": 75,    # Tree list is expensive
            "searchNodes": 30,      # Search operations are moderate
            "expandTreeRow": 50,    # Expanding tree row is moderate
        }
        
        # Define list multipliers (lists can return many items)
        self.list_multipliers = {
            "nodes": 10,           # List of nodes
            "edges": 5,            # List of edges  
            "additionalLines": 2,  # Key-value pairs
            "data": 10,            # Tree list data
            "idValue": 1,          # ID value pairs
            "columns": 2,          # Column data
        }
    
    def validate_query(self, document_ast) -> None:
        """
        Validate a GraphQL query document for complexity.
        
        Args:
            document_ast: The parsed GraphQL query document AST
            
        Raises:
            GraphQLError: If query exceeds complexity limits
        """
        try:
            # Calculate complexity and depth
            complexity = self._calculate_document_complexity(document_ast)
            depth = self._calculate_document_depth(document_ast)
            
            # Log metrics
            logger.info(f"Query complexity: {complexity}, depth: {depth}")
            
            # Check complexity limit
            if complexity > self.max_complexity:
                error_msg = (
                    f"Query complexity {complexity} exceeds maximum allowed "
                    f"complexity of {self.max_complexity}. "
                    f"Please simplify your query by requesting fewer fields or "
                    f"reducing nesting depth."
                )
                logger.warning(error_msg)
                raise GraphQLError(error_msg)
            
            # Check depth limit
            if depth > self.max_depth:
                error_msg = (
                    f"Query depth {depth} exceeds maximum allowed depth of "
                    f"{self.max_depth}. Please reduce query nesting."
                )
                logger.warning(error_msg)
                raise GraphQLError(error_msg)
                
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error validating query complexity: {e}")
            # Don't block queries if validation fails
            pass
    
    def _calculate_document_complexity(self, document_ast) -> int:
        """Calculate total complexity for a document"""
        total_complexity = 0
        
        for definition in document_ast.definitions:
            if isinstance(definition, ast.OperationDefinitionNode):
                total_complexity += self._calculate_selection_set_complexity(
                    definition.selection_set, depth=0
                )
        
        return total_complexity
    
    def _calculate_selection_set_complexity(
        self, 
        selection_set, 
        depth: int,
        parent_multiplier: int = 1
    ) -> int:
        """Calculate complexity for a selection set"""
        if not selection_set:
            return 0
        
        complexity = 0
        
        for selection in selection_set.selections:
            if isinstance(selection, ast.FieldNode):
                field_name = selection.name.value
                
                # Get base field cost
                field_cost = self.expensive_fields.get(
                    field_name, 
                    self.default_field_cost
                )
                
                # Get list multiplier if applicable
                multiplier = self.list_multipliers.get(field_name, 1)
                
                # Apply parent multiplier (for nested lists)
                total_multiplier = parent_multiplier * multiplier
                
                # Add field cost with multiplier
                complexity += field_cost * total_multiplier
                
                # Add nested selections
                if selection.selection_set:
                    complexity += self._calculate_selection_set_complexity(
                        selection.selection_set,
                        depth + 1,
                        total_multiplier
                    )
            
            elif isinstance(selection, ast.InlineFragmentNode):
                if selection.selection_set:
                    complexity += self._calculate_selection_set_complexity(
                        selection.selection_set,
                        depth,
                        parent_multiplier
                    )
            
            elif isinstance(selection, ast.FragmentSpreadNode):
                # Fragment spreads would need fragment definition lookup
                # For now, add a base cost
                complexity += self.default_field_cost
        
        return complexity
    
    def _calculate_document_depth(self, document_ast) -> int:
        """Calculate maximum depth for a document"""
        max_depth = 0
        
        for definition in document_ast.definitions:
            if isinstance(definition, ast.OperationDefinitionNode):
                depth = self._calculate_selection_set_depth(
                    definition.selection_set, 
                    current_depth=0
                )
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_selection_set_depth(
        self, 
        selection_set, 
        current_depth: int
    ) -> int:
        """Calculate maximum depth for a selection set"""
        if not selection_set:
            return current_depth
        
        max_depth = current_depth
        
        for selection in selection_set.selections:
            if isinstance(selection, ast.FieldNode):
                if selection.selection_set:
                    depth = self._calculate_selection_set_depth(
                        selection.selection_set,
                        current_depth + 1
                    )
                    max_depth = max(max_depth, depth)
            
            elif isinstance(selection, ast.InlineFragmentNode):
                if selection.selection_set:
                    depth = self._calculate_selection_set_depth(
                        selection.selection_set,
                        current_depth
                    )
                    max_depth = max(max_depth, depth)
        
        return max_depth


# Create default validator instance
default_complexity_validator = QueryComplexityValidator(
    max_complexity=1000,
    max_depth=10
)
