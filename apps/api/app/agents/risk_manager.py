from app.agents.output_schemas import RiskAssessment
from app.agents.prompts.risk_manager import SYSTEM_PROMPT, build_user_content
from app.llm.client import LLMClient
from app.llm.structured import call_agent


class RiskManagerAgent:
    name = "risk_manager"
    prompt_version = "v1"

    def assess(
        self,
        agent_outputs: list[dict],
        quality_flags: list[str],
        llm: LLMClient,
    ) -> RiskAssessment:
        user_content = build_user_content(agent_outputs, quality_flags)
        return call_agent(
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            response_model=RiskAssessment,
            tool_name="submit_risk_assessment",
            tool_description="Submit your risk assessment of the agent outputs",
        )
