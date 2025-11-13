# Movies Agent Example for E2E Testing
# This example demonstrates using a LangGraph ReAct agent with movie database tools

import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph import NextGenUILangGraphAgent

from .data_set_movies import get_all_movies, search_movie


def create_movies_agent(
    llm: ChatOpenAI,
    system_prompt: str | None = None,
) -> NextGenUILangGraphAgent:
    """Create a movies agent for E2E testing.

    Args:
        llm: LangChain LLM instance to use for the agent
        system_prompt: Optional custom system prompt. If None, uses default.

    Returns:
        NextGenUILangGraphAgent configured for movie queries
    """
    # Default system prompt
    if system_prompt is None:
        system_prompt = (
            "You are a movie database assistant. Use the available tools to search and retrieve movie information. "
            "When a user asks about movies, use get_all_movies() to retrieve all movies, or search_movie(title) for a specific title. "
            "The get_all_movies tool supports filtering by: director, genre, actor, year, min_year, max_year, min_rating. "
            "Always return the complete JSON response from the tool exactly as received."
        )

    # Create ReAct agent with movie tools
    react_agent = create_react_agent(
        llm,
        tools=[search_movie, get_all_movies],
        state_modifier=system_prompt,
    )

    # Wrap in NextGenUILangGraphAgent
    return NextGenUILangGraphAgent(
        agent=react_agent,
        tool_name_with_data="get_all_movies",
    )


async def run_example():
    """Run a simple example of the movies agent."""
    # Get LLM configuration from environment
    llm_model = os.getenv("LLM_MODEL", "llama3.1:8b")
    llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_api_key = os.getenv("LLM_API_KEY", "ollama")

    print("=== Movies Agent Example ===")
    print(f"Model: {llm_model}")
    print(f"Base URL: {llm_base_url}")
    print()

    # Create LLM client
    llm = ChatOpenAI(
        model=llm_model,
        base_url=llm_base_url,
        api_key=llm_api_key,
    )

    # Create movies agent
    movies_agent = create_movies_agent(llm)
    agent_graph = movies_agent.build_graph()

    # Test query
    test_prompt = "Show me Christopher Nolan movies with ratings above 8.5"
    print(f"Query: {test_prompt}\n")

    # Run agent
    result = await agent_graph.ainvoke({"messages": [("user", test_prompt)]})

    # Extract data from result
    print("=== Agent Response ===")
    if result and "messages" in result:
        for msg in result["messages"]:
            if hasattr(msg, "content"):
                print(f"{type(msg).__name__}: {msg.content[:200]}...")

    # Extract final data
    data = movies_agent.extract_data(result)
    print("\n=== Extracted Data ===")
    if data:
        parsed = json.loads(data)
        print(f"Found {len(parsed)} movies:")
        for item in parsed:
            movie = item.get("movie", {})
            print(
                f"  - {movie.get('title')} ({movie.get('year')}) - Rating: {movie.get('imdbRating')}"
            )
    else:
        print("No data extracted")


if __name__ == "__main__":
    asyncio.run(run_example())
