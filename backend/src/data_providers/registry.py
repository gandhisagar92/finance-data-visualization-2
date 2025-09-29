"""
Data provider registry for managing all data providers.
"""

from typing import Dict, Type, Optional
from .base_provider import BaseDataProvider
from .instrument_provider import InstrumentDataProvider
from .listing_provider import ListingDataProvider
from .exchange_provider import ExchangeDataProvider
from .party_provider import PartyDataProvider
from cache.cache_manager import CacheManager


class DataProviderRegistry:
    """Registry for all data providers"""
    
    def __init__(self):
        self._providers: Dict[str, BaseDataProvider] = {}
        self._provider_classes: Dict[str, Type[BaseDataProvider]] = {
            'InstrumentDataProvider': InstrumentDataProvider,
            'ListingDataProvider': ListingDataProvider,
            'ExchangeDataProvider': ExchangeDataProvider,
            'PartyDataProvider': PartyDataProvider
        }
    
    def register_provider(self, name: str, provider: BaseDataProvider):
        """Register a data provider instance"""
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> BaseDataProvider:
        """Get a data provider by name"""
        if name not in self._providers:
            if name in self._provider_classes:
                # Lazy initialization
                provider_class = self._provider_classes[name]
                self._providers[name] = provider_class({})
            else:
                raise ValueError(f"Unknown data provider: {name}")
        
        return self._providers[name]
    
    def initialize_all_providers(self, config: Dict[str, Dict], 
                               cache_manager: Optional[CacheManager] = None):
        """Initialize all providers with configuration and caching"""
        for provider_name, provider_config in config.items():
            if provider_name in self._provider_classes:
                provider_class = self._provider_classes[provider_name]
                
                # Create provider with cache manager if provided
                if cache_manager:
                    provider = provider_class(provider_config)
                    if hasattr(provider, 'cache_manager'):
                        provider.cache_manager = cache_manager
                else:
                    provider = provider_class(provider_config)
                
                self._providers[provider_name] = provider
    
    def get_all_providers(self) -> Dict[str, BaseDataProvider]:
        """Get all registered providers"""
        return self._providers.copy()
