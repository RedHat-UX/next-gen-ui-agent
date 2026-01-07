"""Movies agent invocation for generate endpoint."""

from typing import Any, Optional

from agents import movies_agent
from config import MOVIES_AGENT_RECURSION_LIMIT
from utils.agent_messages import serialize_agent_messages
from utils.logging import log_error, log_info, log_section
from utils.response import create_error_response


def invoke_movies_agent(
    prompt: str,
) -> tuple[Optional[dict], list[dict[str, Any]], Optional[dict]]:
    """
    Invoke the movies agent to fetch data.

    Args:
        prompt: User prompt for the movies agent

    Returns:
        Tuple of (movie_response, agent_messages, error_response)
        If successful, error_response is None.
        If failed, movie_response is None and agent_messages may be empty.
    """
    log_info("Step 1: Invoking movies agent...")

    try:
        movie_response = movies_agent.invoke(
            {"messages": [{"role": "user", "content": prompt.strip()}]},
            {"recursion_limit": MOVIES_AGENT_RECURSION_LIMIT},
        )

        log_info(f"Movies agent response: {movie_response}")
        log_info(f"Number of messages: {len(movie_response.get('messages', []))}")

        # Log message preview
        for i, msg in enumerate(movie_response.get("messages", [])):
            log_info(
                f"Message {i}: Type={type(msg).__name__}, "
                f"Content preview={str(msg)[:200]}"
            )

        # Validate movie response
        if not movie_response or not movie_response.get("messages"):
            return (
                None,
                [],
                create_error_response(
                    "Movies agent failed",
                    "Movies agent returned empty or invalid response",
                    movie_response,
                ),
            )

        # Extract agent messages for debugging
        try:
            messages = movie_response.get("messages", [])
            agent_messages = serialize_agent_messages(messages)
        except Exception as e:
            log_error(f"Warning: Could not serialize agent messages: {e}")
            agent_messages = []

        return movie_response, agent_messages, None

    except Exception as e:
        log_section("MOVIES AGENT ERROR DEBUG")
        log_error(f"Error Type: {type(e).__name__}")
        log_error(f"Error Message: {str(e)}")
        log_error(f"Full Error: {repr(e)}")

        if hasattr(e, "__cause__"):
            log_error(f"Caused by: {e.__cause__}")

        if hasattr(e, "response"):
            log_error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            log_error(f"Response text: {getattr(e.response, 'text', 'N/A')[:500]}")

        return (
            None,
            [],
            create_error_response(
                "Movies agent error", f"Failed to get movie information: {str(e)}"
            ),
        )
