from abc import ABC, abstractmethod

from app.market_data.models import MarketDataBundle


class MarketDataProvider(ABC):
    @abstractmethod
    async def get_bundle(self, ticker: str) -> MarketDataBundle:
        """Fetch all market data needed for agent analysis."""
        ...
