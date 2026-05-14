"""LLM Connector — unified interface for Local + Cloud LLMs.

Strategy:
    - Local: Ollama (qwen2.5:3b) for fast, free inference.
    - Cloud: Groq / OpenAI-compatible for heavier reasoning tasks.

Default: each method raises ``NotImplementedError`` until a provider is wired.
Service code is written to this contract; implement bodies when connecting
Ollama / cloud backends.

TODO:
    - Initialization: Maintain an internal `httpx.AsyncClient` scoped to the
      lifecycle of this class. Call `await client.aclose()` in the `close()` method.
    - `generate` & `generate_chat`: Implement REST calls to Ollama (`/api/generate`
      or `/api/chat`) or the OpenAI-compatible Cloud provider based on the `use_cloud` flag.
    - Streaming: Implement asynchronous generators `generate_stream` and
      `generate_chat_stream` using `httpx` async byte-stream iterators to yield token chunks.
    - Resilience: Fallback to local Ollama if the cloud provider returns 5xx errors
      or rate limits, assuming local hardware supports it.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator


class LLMConnector:
    """Single entry point used by every service that needs an LLM."""

    def __init__(
        self,
        local_base_url: str,
        local_model: str,
        cloud_base_url: str,
        cloud_api_key: str,
        cloud_model: str,
    ) -> None:
        self._local_base_url = local_base_url.rstrip("/")
        self._local_model = local_model
        self._cloud_base_url = cloud_base_url.rstrip("/")
        self._cloud_api_key = cloud_api_key
        self._cloud_model = cloud_model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
        json_mode: bool = False,
    ) -> str:
        """Return a single completion for ``prompt``.

        TODO:
            - Construct the payload: `{"model": self._local_model, "prompt": prompt,
              "system": system, "stream": False}`.
            - If `json_mode` is True, inject JSON formatting requirements into the
              payload (e.g. `{"format": "json"}` for Ollama).
            - Dispatch request via `httpx.AsyncClient.post()` to local/cloud endpoint based on `use_cloud`.
            - Extract and return the raw text completion from the JSON response.
        """
        raise NotImplementedError("LLMConnector.generate is not implemented yet.")

    async def generate_stream(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens for ``prompt`` (real-time TTS pipelines).

        TODO:
            - Set `stream: True` in the payload.
            - Iterate over the `httpx.AsyncClient.stream` response.
            - Parse each JSON-lines chunk, extracting the delta text token.
            - `yield` the token sequentially.
        """
        raise NotImplementedError("LLMConnector.generate_stream is not implemented yet.")
        if False:  # pragma: no cover  - keeps this an async generator
            yield ""

    async def generate_chat(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
        json_mode: bool = False,
    ) -> str:
        """Return one completion given a chat history.

        TODO:
            - Construct the payload according to OpenAI chat format: `{"model": ..., "messages": messages}`.
            - Set `json_mode` if required.
            - Post request and parse `response.json()["choices"][0]["message"]["content"]`.
        """
        raise NotImplementedError("LLMConnector.generate_chat is not implemented yet.")

    async def generate_chat_stream(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens given a chat history.

        TODO:
            - Issue request with `stream: True`.
            - Asynchronously iterate over Server-Sent Events (SSE) or JSON-lines.
            - Yield the text delta from each chunk.
        """
        raise NotImplementedError("LLMConnector.generate_chat_stream is not implemented yet.")
        if False:  # pragma: no cover
            yield ""

    async def close(self) -> None:
        """Release any underlying HTTP client."""
        return None
