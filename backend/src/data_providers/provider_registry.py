"""
Data provider registry and factory.
"""

from typing import Dict, Any
from .stock_provider import StockDataProvider
from .listing_provider import ListingDataProvider
from .exchange_provider import ExchangeDataProvider
from .party_provider import PartyDataProvider
from .option_provider import OptionDataProvider


class DataProviderRegistry:
    """Registry for managing data provider instances"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all data provider instances"""
        # Create instances of each data provider
        self._providers["Stock"] = StockDataProvider(self.config)
        self._providers["Listing"] = ListingDataProvider(self.config)
        self._providers["Exchange"] = ExchangeDataProvider(self.config)
        self._providers["InstrumentParty"] = PartyDataProvider(self.config)
        self._providers["Client"] = PartyDataProvider(self.config)
        self._providers["Option"] = OptionDataProvider(self.config)
    
    def get_provider(self, entity_type: str):
        """Get data provider for a specific entity type"""
        return self._providers.get(entity_type)
    
    def get_all_providers(self) -> Dict[str, Any]:
        """Get all registered providers"""
        return self._providers
