"""Structured output via Anthropic tool_use pattern.

Forces Claude to respond using a tool whose input_schema matches a Pydantic model,
guaranteeing valid JSON output that conforms to the schema.
"""

import json
import logging

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from app.llm.client import LLMClient

logger = logging.getLogger(__name__)


def _pydantic_to_tool(name: str, description: str, model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to an Anthropic tool definition."""
    schema = model.model_json_schema()
    # Remove $defs and other top-level keys that aren't part of input_schema
    clean_schema = {
        "type": "object",
        "properties": schema.get("properties", {}),
        "required": schema.get("required", []),
    }
    # Inline $defs if present
    if "$defs" in schema:
        clean_schema["$defs"] = schema["$defs"]

    return {
        "name": name,
        "description": description,
        "input_schema": clean_schema,
    }


def _create_safe_default(model: type[BaseModel], error: str) -> BaseModel:
    """Create a neutral, zero-confidence fallback output."""
    fields = model.model_fields
    defaults = {}
    for field_name, field_info in fields.items():
        if field_name == "signal":
            defaults[field_name] = "neutral"
        elif field_name == "confidence":
            defaults[field_name] = 0.0
        elif field_name == "score":
            defaults[field_name] = 0.0
        elif field_name == "reasoning":
            defaults[field_name] = f"Agent failed: {error}"
        elif field_name == "risk_level":
            defaults[field_name] = "high"
        elif field_name == "should_block":
            defaults[field_name] = True
        elif field_name == "force_neutral":
            defaults[field_name] = True
        elif field_name == "max_score_allowed":
            defaults[field_name] = 0.0
        elif field_name == "risk_factors":
            defaults[field_name] = [f"Agent failure: {error}"]
        elif field_info.default is not None and field_info.default is not PydanticUndefined:
            defaults[field_name] = field_info.default
        elif field_info.default_factory is not None:
            defaults[field_name] = field_info.default_factory()
        else:
            # Try sensible defaults by type annotation
            annotation = field_info.annotation
            # Handle Optional[X] (Union[X, None]) types
            origin = getattr(annotation, "__origin__", None)
            args = getattr(annotation, "__args__", ())

            if origin is type(int | str):  # types.UnionType (Python 3.10+)
                # e.g. float | None → try the non-None type
                non_none = [a for a in args if a is not type(None)]
                if non_none:
                    annotation = non_none[0]
                else:
                    defaults[field_name] = None
                    continue

            if annotation is str:
                defaults[field_name] = "N/A (agent failed)"
            elif annotation is float:
                defaults[field_name] = 0.0
            elif annotation is int:
                defaults[field_name] = 0
            elif annotation is bool:
                defaults[field_name] = False
            elif origin is list or annotation is list:
                defaults[field_name] = []
            elif origin is dict or annotation is dict:
                defaults[field_name] = {}
            else:
                defaults[field_name] = None

    return model.model_validate(defaults)


def call_agent(
    llm: LLMClient,
    system_prompt: str,
    user_content: str,
    response_model: type[BaseModel],
    tool_name: str = "submit_analysis",
    tool_description: str = "Submit your structured analysis",
    max_retries: int = 3,
) -> BaseModel:
    """Call Claude with forced tool use to get structured output.

    Uses the tool_use pattern: defines a tool matching the Pydantic schema,
    forces Claude to call it, and parses the tool input as the response.
    """
    tool = _pydantic_to_tool(tool_name, tool_description, response_model)

    for attempt in range(max_retries):
        try:
            response = llm.client.messages.create(
                model=llm.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
                tools=[tool],
                tool_choice={"type": "tool", "name": tool_name},
            )

            # Extract tool use block
            for block in response.content:
                if block.type == "tool_use" and block.name == tool_name:
                    return response_model.model_validate(block.input)

            raise ValueError("No tool_use block found in response")

        except Exception as e:
            logger.warning(
                f"Agent call attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt == max_retries - 1:
                logger.error(f"All {max_retries} attempts failed, returning safe default")
                return _create_safe_default(response_model, str(e))

    # Should never reach here
    return _create_safe_default(response_model, "Unknown error")
