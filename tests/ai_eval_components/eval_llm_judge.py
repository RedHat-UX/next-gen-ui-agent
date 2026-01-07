"""LLM-as-a-Judge evaluation for UI component selection."""

import asyncio
import json

from ai_eval_components.types import JudgeResult
from next_gen_ui_agent.component_selection_chart_instructions import CHART_INSTRUCTIONS
from next_gen_ui_agent.component_selection_common import UI_COMPONENTS_DESCRIPTION_ALL
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata

# Default model for judges (can be overridden by JUDGE_MODEL env var)
JUDGE_MODEL_DEFAULT = "granite3.3:2b"
# Category-to-score mappings for consistent evaluation
FIELD_RELEVANCE_CATEGORIES = {
    "perfectly_relevant": 1.0,
    "relevant_with_supporting_detail": 0.85,
    "partially_relevant": 0.5,
    "irrelevant": 0.2,
}

COMPONENT_CHOICE_CATEGORIES = {
    "perfect_choice": 1.0,
    "good_choice": 0.85,
    "reasonable_choice": 0.65,
    "wrong_choice": 0.3,
}


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
    category_mapping: dict[str, float],
) -> JudgeResult:
    """
    Common judge execution logic.

    Parameters:
    * judge_name - identifier for this judge
    * prompt - prompt to send to judge LLM
    * inference - inference instance for judge
    * threshold - minimum score to pass (0.0-1.0)
    * category_mapping - dict mapping category names to scores

    Returns JudgeResult dict.
    """
    try:
        response = await inference.call_model(
            "You are a helpful AI judge evaluating UI component selections.", prompt
        )
        result = json.loads(response)

        # Map category to score
        category = result["category"]
        score = category_mapping.get(category)

        if score is None:
            # Unknown category - log warning and use neutral score
            print(
                f"   WARNING: Judge '{judge_name}' returned unexpected category: '{category}'"
            )
            print(f"   Expected one of: {list(category_mapping.keys())}")
            print(f"   Judge response: {response[:200]}")
            score = 0.5  # Default to neutral

        return {
            "judge_name": judge_name,
            "category": category,
            "score": score,
            "passed": score >= threshold,
            "reasoning": result["reason"],
        }
    except Exception as e:
        # If judge fails, log error and return neutral result
        print(f"   ERROR: Judge '{judge_name}' failed to execute")
        print(f"   Exception: {type(e).__name__}: {str(e)}")
        if hasattr(e, "__traceback__"):
            import traceback

            print(f"   Traceback: {traceback.format_exc()}")
        return {
            "judge_name": judge_name,
            "category": "judge_error",
            "score": 0.5,
            "passed": False,
            "reasoning": f"Judge execution error: {type(e).__name__}: {str(e)}",
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

    prompt = f"""Evaluate if the selected fields are appropriate for VISUALIZING the AVAILABLE DATA in the chosen COMPONENT TYPE to answer the user's question.

Your task: Judge whether the fields chosen for visualization are relevant, complete, and appropriate for displaying in a {component.component} component.

USER QUESTION: {user_prompt}

AVAILABLE DATA (from backend API):
{backend_data_str}

SELECTED FIELDS (to visualize in UI):
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

Evaluate and select ONE category that best describes the field selection:

Categories (choose exactly one):
- "perfectly_relevant" - All fields directly answer the question with no missing data
- "relevant_with_supporting_detail" - Fields are relevant with appropriate supporting details
- "partially_relevant" - Fields partially address the request but missing key data
- "irrelevant" - Fields don't address user request or completely irrelevant

Reply ONLY with valid JSON in this exact format (no markdown, no code blocks, just raw JSON):
{{"category": "relevant_with_supporting_detail", "reason": "brief explanation of your evaluation"}}"""

    return await run_judge(
        "field_relevance",
        prompt,
        inference,
        0.7,
        FIELD_RELEVANCE_CATEGORIES,  # Pass category mapping
    )


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

Available UI Components (complete list):

{UI_COMPONENTS_DESCRIPTION_ALL}

{CHART_INSTRUCTIONS}

Semantic Selection Guidelines (domain-agnostic):

When user asks for SINGULAR visual/item:
- "poster", "image", "logo", "diagram" -> image component
- "details", "information", "status", "about X" -> one-card component
- "trailer", "video", "promo" -> video-player component

When user asks for MULTIPLE items/comparison:
- "list of", "show all", "what are the" -> set-of-cards or table
- "compare", "which ones", "data on" -> table

When user asks for NUMERIC COMPARISONS or TRENDS:
- "compare [metric]" -> chart-bar or table
- "trend over time", "[metric] by week/month" -> chart-line
- "distribution of", "breakdown by", "percentage of" -> chart-pie or chart-donut
- "A vs B", "compare [metric1] and [metric2]" -> chart-mirrored-bar

Cross-Domain Examples:

Movies:
- "Show me the poster" -> image = GOOD | one-card = OK (works but overkill)
- "Movie details" -> one-card = GOOD
- "List of actors" -> set-of-cards = GOOD
- "Compare movie revenues" -> chart-bar = GOOD | table = OK
- "Revenue trend by week" -> chart-line = GOOD
- "Genre distribution" -> chart-pie = GOOD | chart-donut = GOOD
- "Budget vs Revenue" -> chart-mirrored-bar = GOOD

Kubernetes:
- "Cluster status" -> one-card = GOOD
- "Show namespace diagram" -> image = GOOD
- "List failing pods" -> set-of-cards = GOOD | table = GOOD
- "Compare node resources" -> table = GOOD | chart-bar = OK
- "Pod details" -> one-card = GOOD
- "CPU usage over time" -> chart-line = GOOD

Subscriptions:
- "User subscription info" -> one-card = GOOD
- "All active subscriptions" -> set-of-cards = GOOD | table = GOOD
- "Subscription details" -> one-card = GOOD
- "Subscription cost comparison" -> chart-bar = GOOD | table = OK
- "Active subscriptions by category" -> chart-pie = GOOD

Evaluate and select ONE category that best describes the component choice:

Categories (choose exactly one):
- "perfect_choice" - Perfect component type for this use case
- "good_choice" - Good choice, clearly appropriate
- "reasonable_choice" - Reasonable but not ideal choice
- "wrong_choice" - Wrong component type for this use case

Reply ONLY with valid JSON in this exact format (no markdown, no code blocks, just raw JSON):
{{"category": "good_choice", "reason": "brief explanation of your evaluation"}}"""

    return await run_judge(
        "component_choice",
        prompt,
        inference,
        0.8,
        COMPONENT_CHOICE_CATEGORIES,  # Pass category mapping
    )


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
