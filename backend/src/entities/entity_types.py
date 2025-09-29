"""
Entity type classes for financial data relationship explorer.
Each entity type represents a specific financial data object with its own properties and methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseEntity(ABC):
    """Base class for all entity types"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.id = self._get_primary_id()
        self.entity_type = self.__class__.__name__
    
    @abstractmethod
    def _get_primary_id(self) -> str:
        """Get the primary identifier for this entity"""
        pass
    
    @abstractmethod
    def to_node_dict(self) -> Dict[str, Any]:
        """Convert entity to node representation for graph"""
        pass
    
    def get_field_value(self, field_name: str) -> Any:
        """Get field value from entity data"""
        return self.data.get(field_name)


class Stock(BaseEntity):
    """Stock entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('instrumentId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('instrument_type', 'Stock'),
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Instrument Id": self.data.get('instrumentId'),
                "ISIN": self.data.get('isin'),
                "Primary Trading Line": self.data.get('primaryTradingLine'),
                "Sector": self.data.get('sector')
            },
            "refDataType": "Stock",
            "idType": "instrumentId",
            "idValue": {"instrumentId": self.id},
            "asOf": datetime.now().isoformat()
        }
    
    @property
    def instrument_id(self) -> str:
        return self.data.get('instrumentId', '')
    
    @property
    def name(self) -> str:
        return self.data.get('name', '')
    
    @property
    def isin(self) -> str:
        return self.data.get('isin', '')


class Option(BaseEntity):
    """Option entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('instrumentId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('instrument_type', 'Option'),
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Instrument Id": self.data.get('instrumentId'),
                "Option Type": self.data.get('optionType'),
                "Strike": self.data.get('strike'),
                "Expiration Date": self.data.get('expirationDate'),
                "Underlying": self.data.get('underlyingInstrumentId')
            },
            "refDataType": "Option",
            "idType": "instrumentId",
            "idValue": {"instrumentId": self.id},
            "asOf": datetime.now().isoformat()
        }
    
    @property
    def underlying_instrument_id(self) -> str:
        return self.data.get('underlyingInstrumentId', '')


class Future(BaseEntity):
    """Future contract entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('instrumentId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('instrument_type', 'Future'),
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Instrument Id": self.data.get('instrumentId'),
                "Underlying Asset": self.data.get('underlyingAsset'),
                "Expiration Date": self.data.get('expirationDate'),
                "Contract Size": self.data.get('contractSize'),
                "Settlement Type": self.data.get('settlementType')
            },
            "refDataType": "Future",
            "idType": "instrumentId", 
            "idValue": {"instrumentId": self.id},
            "asOf": datetime.now().isoformat()
        }
    
    @property
    def underlying_asset_id(self) -> str:
        return self.data.get('underlyingAssetId', '')
    
    @property
    def expiration_date(self) -> str:
        return self.data.get('expirationDate', '')


class Bond(BaseEntity):
    """Bond entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('instrumentId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('instrument_type', 'Bond'),
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Instrument Id": self.data.get('instrumentId'),
                "ISIN": self.data.get('isin'),
                "Coupon Rate": self.data.get('couponRate'),
                "Maturity Date": self.data.get('maturityDate'),
                "Credit Rating": self.data.get('creditRating')
            },
            "refDataType": "Bond",
            "idType": "instrumentId",
            "idValue": {"instrumentId": self.id},
            "asOf": datetime.now().isoformat()
        }


class Listing(BaseEntity):
    """Listing/Trading Line entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('tradingLineId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": "Trading Line",
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Trading Line Id": self.data.get('tradingLineId'),
                "RIC": self.data.get('ric'),
                "BBG Ticker": self.data.get('bloombergTicker'),
                "Exchange": self.data.get('exchangeId')
            },
            "refDataType": "Listing",
            "idType": "tradingLineId",
            "idValue": {"tradingLineId": self.id},
            "asOf": datetime.now().isoformat()
        }


class Exchange(BaseEntity):
    """Exchange entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('exchangeId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('exchangeCode', ''),
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Settlement Days": self.data.get('settlementDays'),
                "Venue ID": self.data.get('venueId'),
                "Currency": self.data.get('currency')
            },
            "refDataType": "Exchange",
            "idType": "exchangeId",
            "idValue": {"exchangeId": self.id},
            "asOf": datetime.now().isoformat()
        }


class InstrumentParty(BaseEntity):
    """Instrument Party entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('instrumentPartyId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": "Instrument Party",
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "IPARTY": self.data.get('instrumentPartyId'),
                "ECI": self.data.get('eci'),
                "Entity Type": self.data.get('entityType')
            },
            "refDataType": "InstrumentParty",
            "idType": "instrumentPartyId",
            "idValue": {"instrumentPartyId": self.id},
            "asOf": datetime.now().isoformat()
        }


class Client(BaseEntity):
    """Client/Party entity type"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('clientId', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": "Client",
            "titleLine2": self.data.get('name', ''),
            "status": self.data.get('status', 'UNKNOWN'),
            "additionalLines": {
                "Client ID": self.data.get('clientId'),
                "ECI": self.data.get('eci'),
                "LEI": self.data.get('lei'),
                "Client Type": self.data.get('clientType')
            },
            "refDataType": "Client",
            "idType": "clientId",
            "idValue": {"clientId": self.id},
            "asOf": datetime.now().isoformat()
        }


class TreeListNode(BaseEntity):
    """Special node type for expensive relationships displayed as tree-list"""
    
    def _get_primary_id(self) -> str:
        return self.data.get('id', '')
    
    def to_node_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titleLine1": self.data.get('titleLine1', ''),
            "titleLine2": self.data.get('titleLine2', ''),
            "status": self.data.get('status', 'ACTIVE'),
            "additionalLines": {
                "Total Count": str(self.data.get('totalCount', 0))
            },
            "refDataType": self.data.get('targetType', ''),
            "idType": "treeList",
            "idValue": {
                "sourceEntityId": self.data.get('sourceEntityId'),
                "relationshipName": self.data.get('relationshipName')
            },
            "asOf": datetime.now().isoformat(),
            "displayType": "tree-list"
        }
    
    @property
    def source_entity_id(self) -> str:
        return self.data.get('sourceEntityId', '')
    
    @property
    def relationship_name(self) -> str:
        return self.data.get('relationshipName', '')
    
    @property
    def target_type(self) -> str:
        return self.data.get('targetType', '')
