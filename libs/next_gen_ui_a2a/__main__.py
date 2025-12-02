import argparse
import logging

import uvicorn  # pants: no-infer-dep
from a2a.server.apps import A2AStarletteApplication  # pants: no-infer-dep
from a2a.server.request_handlers import DefaultRequestHandler  # pants: no-infer-dep
from a2a.server.tasks import InMemoryTaskStore  # pants: no-infer-dep
from next_gen_ui_a2a.agent_card import card
from next_gen_ui_a2a.agent_executor import NextGenUIAgentExecutor
from next_gen_ui_agent.agent_config import (
    add_agent_config_comandline_args,
    read_agent_config_dict_from_arguments,
)
from next_gen_ui_agent.argparse_env_default_action import EnvDefault
from next_gen_ui_agent.inference.inference_builder import (
    PROVIDER_OPENAI,
    add_inference_comandline_args,
    create_inference_from_arguments,
)
from next_gen_ui_agent.types import AgentConfig

logger = logging.getLogger("NextGenUI-A2A-Server")

if __name__ == "__main__":
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Next Gen UI A2A Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Run with OpenAI inference
  python -m next_gen_ui_a2a --model gpt-3.5-turbo --api-key=XYZ

  # Run with OpenAI API of Ollama (local) on defined host and port
  python -m next_gen_ui_a2a --host 127.0.0.1 --port 8000 --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama

  # Run with LlamaStack inference on default host and port
  python -m next_gen_ui_a2a --provider openai --model llama3.2-3b --base-url http://localhost:5001/v1

""",
    )

    add_agent_config_comandline_args(parser)

    add_inference_comandline_args(parser, default_provider=PROVIDER_OPENAI)

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        required=True,
        help="Host to bind to",
        action=EnvDefault,
        envvar="A2A_HOST",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        required=True,
        help="Port to bind to",
        action=EnvDefault,
        envvar="A2A_PORT",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    config_dict = read_agent_config_dict_from_arguments(args, logger)
    config = AgentConfig(**config_dict)

    logger.info(
        "Starting Next Gen UI A2A Server at host %s and port %s, debug=%s",
        args.host,
        args.port,
        args.debug,
    )

    inference = create_inference_from_arguments(parser, args, logger)

    request_handler = DefaultRequestHandler(
        agent_executor=NextGenUIAgentExecutor(config=config, inference=inference),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host=args.host, port=args.port)
