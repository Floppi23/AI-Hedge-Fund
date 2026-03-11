from app.agents.base import BaseAgent
from app.agents.output_schemas import SentimentOutput
from app.agents.prompts.sentiment import SYSTEM_PROMPT, build_user_content
from app.llm.client import LLMClient
from app.llm.structured import call_agent
from app.market_data.models import MarketDataBundle


class SentimentAgent(BaseAgent):
    name = "sentiment"
    prompt_version = "v1"

    def analyze(
        self,
        ticker: str,
        market_data: MarketDataBundle,
        llm: LLMClient,
    ) -> SentimentOutput:
        user_content = build_user_content(ticker, market_data)
        return call_agent(
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            response_model=SentimentOutput,
            tool_name="submit_sentiment_analysis",
            tool_description="Submit your sentiment analysis of the stock",
        )
