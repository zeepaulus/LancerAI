"""LLM Connector — unified interface for Local + Cloud LLMs.

Strategy:
    - Local: Ollama (qwen2.5:3b) for fast, free inference.
    - Cloud: Groq / OpenAI-compatible for heavier reasoning tasks.

Default: each method raises ``NotImplementedError`` until a provider is wired.
Service code is written to this contract; implement bodies when connecting
Ollama / cloud backends.

TODO:
    - Implement ``generate`` (one-shot) against Ollama ``/api/generate``.
    - Implement ``generate_stream`` for token streaming (used by voice TTS).
    - Implement ``generate_chat`` + ``generate_chat_stream`` for chat history.
    - Add cloud fallback path keyed off ``cloud_api_key``.
    - Manage a single ``httpx.AsyncClient`` with proper close().
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
        """Return a single completion for ``prompt``."""
        raise NotImplementedError("LLMConnector.generate is not implemented yet.")

    async def generate_stream(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens for ``prompt`` (real-time TTS pipelines)."""
        raise NotImplementedError("LLMConnector.generate_stream is not implemented yet.")
        if False:  # pragma: no cover  - keeps this an async generator
            yield ""

    async def generate_chat(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
        json_mode: bool = False,
    ) -> str:
        """Return one completion given a chat history."""
        raise NotImplementedError("LLMConnector.generate_chat is not implemented yet.")

    async def generate_chat_stream(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens given a chat history."""
        raise NotImplementedError("LLMConnector.generate_chat_stream is not implemented yet.")
        if False:  # pragma: no cover
            yield ""

    async def close(self) -> None:
        """Release any underlying HTTP client."""
        return None
