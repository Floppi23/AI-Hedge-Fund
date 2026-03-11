"""Core orchestration: execute a research run through the full agent pipeline."""

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from app.agents.fundamentals import FundamentalsAgent
from app.agents.output_schemas import AgentSignalOutput
from app.agents.risk_manager import RiskManagerAgent
from app.agents.sentiment import SentimentAgent
from app.agents.technicals import TechnicalsAgent
from app.agents.valuation import ValuationAgent
from app.config import Settings
from app.db.engine import get_session_factory
from app.llm.client import LLMClient
from app.market_data.mock_provider import MockMarketDataProvider
from app.models.agent_output import AgentOutput
from app.models.final_signal import FinalSignal
from app.repositories.agent_output import AgentOutputRepository
from app.repositories.final_signal import FinalSignalRepository
from app.repositories.research_run import ResearchRunRepository
from app.services.signal_service import aggregate_signals

logger = logging.getLogger(__name__)

# Core signal agents (run in parallel via thread pool)
CORE_AGENTS = [
    FundamentalsAgent(),
    ValuationAgent(),
    TechnicalsAgent(),
    SentimentAgent(),
]


def _run_single_agent(agent, ticker, market_data, llm):
    """Run a single agent, catching exceptions."""
    try:
        result = agent.analyze(ticker, market_data, llm)
        return {"agent": agent, "result": result, "error": None}
    except Exception as e:
        logger.error(f"Agent {agent.name} failed: {e}")
        return {"agent": agent, "result": None, "error": str(e)}


async def execute_run_pipeline(run_id, settings: Settings):
    """The main worker flow for a research run.

    1. Set status to running
    2. Fetch market data
    3. Run 4 core agents (via thread pool for sync LLM calls)
    4. Validate and save agent outputs
    5. Run risk manager
    6. Aggregate signals
    7. Save final signal
    8. Set status to completed/blocked/failed
    """
    factory = get_session_factory(settings)

    async with factory() as session:
        run_repo = ResearchRunRepository(session)
        agent_repo = AgentOutputRepository(session)
        signal_repo = FinalSignalRepository(session)

        try:
            # 1. Set running
            await run_repo.update_status(run_id, "running")
            await session.commit()

            run = await run_repo.get_by_id(run_id)
            if run is None:
                logger.error(f"Run {run_id} not found")
                return

            ticker = run.asset_id

            # 2. Fetch market data
            provider = MockMarketDataProvider()
            market_data = await provider.get_bundle(ticker)

            # 3. Run core agents via ThreadPoolExecutor (LLM calls are sync)
            llm = LLMClient(
                api_key=settings.anthropic_api_key,
                model=settings.model_name,
            )

            # Run agents concurrently in threads
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for agent in CORE_AGENTS:
                    future = executor.submit(
                        _run_single_agent, agent, ticker, market_data, llm
                    )
                    futures.append(future)

                agent_results_raw = [f.result() for f in futures]

            # 4. Validate and save agent outputs
            agent_results = []
            for item in agent_results_raw:
                agent = item["agent"]
                result = item["result"]
                error = item["error"]

                if result is not None and isinstance(result, AgentSignalOutput):
                    is_valid = True
                    validation_errors = None
                    output_dict = result.model_dump()

                    # Consistency check: score direction matches signal
                    if result.signal == "bullish" and result.score < -0.1:
                        is_valid = False
                        validation_errors = {"inconsistency": "bullish signal but negative score"}
                    elif result.signal == "bearish" and result.score > 0.1:
                        is_valid = False
                        validation_errors = {"inconsistency": "bearish signal but positive score"}
                else:
                    is_valid = False
                    validation_errors = {"error": error or "No result returned"}
                    output_dict = {"error": error or "No result"}

                agent_output = AgentOutput(
                    run_id=run_id,
                    agent_name=agent.name,
                    prompt_version=agent.prompt_version,
                    model_version=settings.model_name if agent.name != "technicals" else "deterministic",
                    stance=result.signal if result else None,
                    score=result.score if result else None,
                    confidence=result.confidence if result else None,
                    is_valid=is_valid,
                    validation_errors=validation_errors,
                    output_json=output_dict,
                )
                await agent_repo.create(agent_output)

                agent_results.append({
                    "agent_name": agent.name,
                    "stance": result.signal if result else None,
                    "score": result.score if result else 0.0,
                    "confidence": result.confidence if result else 0.0,
                    "is_valid": is_valid,
                    "reasoning": result.reasoning if result else error,
                })

            await session.commit()

            # 5. Run risk manager
            risk_agent = RiskManagerAgent()
            risk_assessment = risk_agent.assess(
                agent_outputs=agent_results,
                quality_flags=market_data.quality_flags,
                llm=llm,
            )

            # 6. Aggregate signals
            final_data = aggregate_signals(agent_results, risk_assessment)

            # 7. Save final signal
            final_signal = FinalSignal(
                run_id=run_id,
                **final_data,
            )
            await signal_repo.create(final_signal)

            # 8. Set final status
            final_status = "blocked" if final_data["release_status"] == "blocked" else "completed"
            await run_repo.update_status(run_id, final_status)
            await session.commit()

            logger.info(
                f"Run {run_id} finished: {final_status}, "
                f"signal={final_data['final_stance']}, "
                f"release={final_data['release_status']}"
            )

        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}\n{traceback.format_exc()}")
            await session.rollback()
            async with factory() as err_session:
                err_repo = ResearchRunRepository(err_session)
                await err_repo.update_status(run_id, "failed", error_message=str(e))
                await err_session.commit()
