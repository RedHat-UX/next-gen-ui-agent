import asyncio

import aiohttp
from next_gen_ui_agent.inference.inference_base import InferenceBase


class ProxiedAnthropicVertexAIInference(InferenceBase):
    """
    Custom inference implementation for calling Claude models from Google Vertex AI
    using a proxied Anthropic Vertex AI API endpoint.

    This implementation makes HTTP requests to a proxy service that forwards
    requests to Claude models from Google Vertex AI using the Anthropic Vertex API format.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        temperature: float = 0.0,
        anthropic_version: str = "vertex-2023-10-16",
        max_tokens: int = 4096,
    ):
        """
        Initialize the ProxiedAnthropicVertexAIInference.

        Final url to call is constructed as `"{base_url}/models/{model}:streamRawPredict"`.

        Args:
            base_url: Base API URL (e.g., "https://api.example.com/haiku").
            model: Model identifier (e.g., "claude-3-5-haiku-20241022")
            api_key: Bearer token for authentication
            temperature: Temperature parameter for model (default 0 for deterministic output)
            anthropic_version: Anthropic API version string (default "vertex-2023-10-16")
            max_tokens: Maximum number of tokens to generate (default 4096)
        """
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.anthropic_version = anthropic_version
        self.max_tokens = max_tokens

    async def call_model(self, system_msg: str, prompt: str) -> str:
        """
        Call the proxied Anthropic Vertex AI API with the given system message and prompt.

        Args:
            system_msg: System message to set the context for the model
            prompt: User prompt/query

        Returns:
            str: Text response from the model

        Raises:
            aiohttp.ClientError: If the HTTP request fails (after 10 retries in 10s intervals for 429 errors)
            ValueError: If the response format is invalid or missing expected content
            json.JSONDecodeError: If the response cannot be parsed as JSON
        """
        # Build the request URL
        url = f"{self.base_url}/models/{self.model}:streamRawPredict"

        # Build messages array with system and user messages
        messages = [
            {"role": "user", "content": [{"type": "text", "text": system_msg}]},
            {"role": "user", "content": [{"type": "text", "text": prompt}]},
        ]

        # Construct request body
        request_body = {
            "anthropic_version": self.anthropic_version,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Retry logic for rate limiting (HTTP 429)
        max_retries = 10
        retry_delay = 10  # seconds

        for attempt in range(max_retries + 1):
            # Make the async HTTP POST request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=request_body, headers=headers
                ) as response:
                    # Check for rate limiting (HTTP 429)
                    if response.status == 429:
                        error_text = await response.text()
                        if "Usage limit exceeded" in error_text:
                            if attempt < max_retries:
                                # Wait and retry
                                await asyncio.sleep(retry_delay)
                                continue
                            else:
                                # Max retries exceeded
                                raise aiohttp.ClientError(
                                    f"HTTP 429 error after {max_retries} retries: {error_text}"
                                )
                        else:
                            # Other 429 error, don't retry
                            raise aiohttp.ClientError(f"HTTP 429 error: {error_text}")

                    # Check for other HTTP errors
                    if response.status != 200:
                        error_text = await response.text()
                        raise aiohttp.ClientError(
                            f"HTTP {response.status} error: {error_text}"
                        )

                    # Parse JSON response
                    response_data = await response.json()

            # Extract text from the first content part
            try:
                content = response_data.get("content", [])
                if not content:
                    raise ValueError("Response does not contain any content")

                first_content = content[0]
                text: str = first_content.get("text")

                if text is None:
                    raise ValueError(
                        f"First content part does not contain 'text' field: {first_content}"
                    )

                return text

            except (KeyError, IndexError, TypeError) as e:
                raise ValueError(
                    f"Invalid response format. Expected content[0].text but got: {response_data}"
                ) from e

        # This should never be reached due to exception handling above
        raise aiohttp.ClientError(
            "Unexpected error: loop completed without returning or raising"
        )
