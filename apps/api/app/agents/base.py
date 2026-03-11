from abc import ABC, abstractmethod

from app.agents.output_schemas import AgentSignalOutput
from app.llm.client import LLMClient
from app.market_data.models import MarketDataBundle


class BaseAgent(ABC):
    """All signal-producing agents implement this interface."""

    name: str
    prompt_version: str = "v1"

    @abstractmethod
    def analyze(
        self,
        ticker: str,
        market_data: MarketDataBundle,
        llm: LLMClient,
    ) -> AgentSignalOutput:
        """Run analysis and return a validated structured output."""
        ...
