from app.agents.base import BaseAgent
from app.agents.output_schemas import FundamentalsOutput
from app.agents.prompts.fundamentals import SYSTEM_PROMPT, build_user_content
from app.llm.client import LLMClient
from app.llm.structured import call_agent
from app.market_data.models import MarketDataBundle


class FundamentalsAgent(BaseAgent):
    name = "fundamentals"
    prompt_version = "v1"

    def analyze(
        self,
        ticker: str,
        market_data: MarketDataBundle,
        llm: LLMClient,
    ) -> FundamentalsOutput:
        user_content = build_user_content(ticker, market_data)
        return call_agent(
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            response_model=FundamentalsOutput,
            tool_name="submit_fundamentals_analysis",
            tool_description="Submit your fundamental analysis of the stock",
        )
