"""LLM-as-a-Judge evaluation for UI component selection."""

import asyncio
import json

from ai_eval_components.types import JudgeResult
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata

# Default model for judges (can be overridden by JUDGE_MODEL env var)
JUDGE_MODEL_DEFAULT = "granite3.3:2b"


def _truncate_backend_data(backend_data: dict, max_length: int = 1000) -> str:
    """Truncate backend data for LLM prompts."""
    backend_data_str = json.dumps(backend_data, indent=2)
    if len(backend_data_str) > max_length:
        return backend_data_str[:max_length] + "\n... (truncated)"
    return backend_data_str


async def run_judge(
    judge_name: str,
    prompt: str,
    inference: InferenceBase,
    threshold: float,
) -> JudgeResult:
    """
    Common judge execution logic.

    Parameters:
    * judge_name - identifier for this judge
    * prompt - prompt to send to judge LLM
    * inference - inference instance for judge
    * threshold - minimum score to pass (0.0-1.0)

    Returns JudgeResult dict.
    """
    try:
        response = await inference.call_model(
            "You are a helpful AI judge evaluating UI component selections.", prompt
        )
        result = json.loads(response)
        return {
            "judge_name": judge_name,
            "score": float(result["score"]),
            "passed": float(result["score"]) >= threshold,
            "reasoning": result["reason"],
        }
    except Exception as e:
        # If judge fails, return neutral result
        return {
            "judge_name": judge_name,
            "score": 0.5,
            "passed": False,
            "reasoning": f"Judge error: {str(e)}",
        }


async def judge_field_relevance(
    component: UIComponentMetadata,
    user_prompt: str,
    backend_data: dict,
    inference: InferenceBase,
) -> JudgeResult:
    """
    Judge if selected fields are relevant to user's question.
    Domain-agnostic with cross-domain examples.
    Threshold: 0.7
    """
    fields_info = [{"name": f.name, "data_path": f.data_path} for f in component.fields]

    backend_data_str = _truncate_backend_data(backend_data)

    prompt = f"""Evaluate if the selected fields are relevant to answering the user's question.

USER QUESTION: {user_prompt}

AVAILABLE DATA:
{backend_data_str}

SELECTED FIELDS:
{json.dumps(fields_info, indent=2)}

COMPONENT TYPE: {component.component}

Cross-Domain Examples of GOOD field selections:

Movies:
- "show poster" + one-card -> Image + Title + Year = GOOD (metadata enhances card)
- "movie rating" + one-card -> Title + Rating + Votes = GOOD (addresses request)

Kubernetes:
- "cluster status" + one-card -> Name + Status + Nodes + Version = GOOD (comprehensive)
- "pod details" + one-card -> Name + Status + Namespace + CPU = GOOD (relevant details)
- "failing pods" + set-of-cards -> Name + Status + Error + Namespace = GOOD

Subscriptions:
- "subscription info" + one-card -> Name + Status + EndDate + Price = GOOD

Cross-Domain Examples of BAD field selections:

Movies:
- "poster" + one-card -> Title + Revenue BUT NO Image = BAD (missing main field)
- "actor names" + one-card -> Title + Budget = BAD (doesn't address request)

Kubernetes:
- "cluster status" + one-card -> Name + Budget + Revenue = BAD (irrelevant fields)
- "pod CPU usage" + one-card -> Name + Status BUT NO CPU = BAD (missing requested data)

Subscriptions:
- "subscription end date" + one-card -> Name + Description BUT NO EndDate = BAD

Score how well these fields answer the user's question on a scale of 0.0 to 1.0:
- 1.0 = perfectly relevant fields that directly answer the question
- 0.7-0.9 = fields are relevant with appropriate supporting details
- 0.4-0.6 = fields partially relevant but missing key data
- 0.0-0.3 = fields don't address user request or completely irrelevant

Reply ONLY with valid JSON in this exact format:
{{"score": 0.85, "reason": "brief explanation of your scoring"}}"""

    return await run_judge("field_relevance", prompt, inference, 0.7)


async def judge_component_choice(
    component: UIComponentMetadata,
    user_prompt: str,
    backend_data: dict,
    inference: InferenceBase,
) -> JudgeResult:
    """
    Judge if the chosen component type is semantically appropriate.
    Domain-agnostic with cross-domain examples.
    Threshold: 0.8
    """
    backend_data_str = _truncate_backend_data(backend_data)

    prompt = f"""Evaluate if the chosen UI component type is appropriate for the user's request and data structure.

USER REQUEST: {user_prompt}

DATA STRUCTURE:
{backend_data_str}

CHOSEN COMPONENT: {component.component}

Semantic Component Guidelines (domain-agnostic):

When user asks for SINGULAR visual/item:
- "poster", "image", "logo", "diagram" -> image component
- "details", "information", "status", "about X" -> one-card component

When user asks for MULTIPLE items/comparison:
- "list of", "show all", "what are the" -> set-of-cards or table
- "compare", "which ones", "data on" -> table

Cross-Domain Examples:

Movies:
- "Show me the poster" -> image = GOOD | one-card = OK (works but overkill)
- "Movie details" -> one-card = GOOD
- "List of actors" -> set-of-cards = GOOD

Kubernetes:
- "Cluster status" -> one-card = GOOD
- "Show namespace diagram" -> image = GOOD
- "List failing pods" -> set-of-cards = GOOD | table = GOOD
- "Compare node resources" -> table = GOOD
- "Pod details" -> one-card = GOOD

Subscriptions:
- "User subscription info" -> one-card = GOOD
- "All active subscriptions" -> set-of-cards = GOOD | table = GOOD
- "Subscription details" -> one-card = GOOD

Score how appropriate this component choice is on a scale of 0.0 to 1.0:
- 1.0 = perfect component choice
- 0.8-0.9 = good choice, clearly appropriate
- 0.5-0.7 = reasonable but not ideal
- 0.0-0.4 = wrong component type

Reply ONLY with valid JSON in this exact format:
{{"score": 0.90, "reason": "brief explanation of your scoring"}}"""

    return await run_judge("component_choice", prompt, inference, 0.8)


async def run_llm_judges(
    component: UIComponentMetadata,
    user_prompt: str,
    backend_data: dict,
    judge_inference: InferenceBase | None = None,
) -> list[JudgeResult] | None:
    """
    Run all LLM judges in parallel and return results.

    Parameters:
    * judge_inference - Inference instance for judges (should be pre-initialized)

    Returns list of JudgeResult dicts, or None if judges disabled or inference not available.
    """
    if judge_inference is None:
        print("Judge inference not available, skipping judges")
        return None

    print(f"Running judges for component: {component.component}")
    try:

        # Run both judges in parallel
        judge_results = await asyncio.gather(
            judge_field_relevance(
                component, user_prompt, backend_data, judge_inference
            ),
            judge_component_choice(
                component, user_prompt, backend_data, judge_inference
            ),
        )

        print(f"Judges completed: {len(judge_results)} results")
        return list(judge_results)

    except Exception as e:
        # Judge failures are non-fatal
        print(f"Judge execution error: {e}")
        return None
