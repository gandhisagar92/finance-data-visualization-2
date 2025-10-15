"""
Configuration package.
"""

from .config_manager import ConfigurationManager
from .entity_definition import specific_entity_definition
from .relationship_definition import relationship_definition

__all__ = [
    'ConfigurationManager',
    'specific_entity_definition',
    'relationship_definition'
]
