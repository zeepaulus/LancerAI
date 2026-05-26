"""LLM Connector — unified interface for Local + Cloud LLMs.

Strategy:
    - Local: Ollama (OpenAI-compatible /v1/chat/completions endpoint).
    - Cloud: Groq / OpenAI-compatible for heavier reasoning tasks.

Both paths use the same OpenAI chat format. The ``use_cloud`` flag selects
which base URL and API key are used for each call.

Streaming is implemented via Server-Sent Events (SSE) iteration with
``httpx.AsyncClient.stream``, yielding text deltas token by token.
"""

from __future__ import annotations

import json
import logging
import typing
from collections.abc import AsyncGenerator

import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)


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
        self._client = httpx.AsyncClient(timeout=_TIMEOUT)

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def has_cloud(self) -> bool:
        """True when a cloud API key is configured."""
        return bool(self._cloud_api_key)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _chat_url(self, use_cloud: bool) -> str:
        base = self._cloud_base_url if use_cloud else self._local_base_url
        return f"{base}/v1/chat/completions"

    def _headers(self, use_cloud: bool) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if use_cloud and self._cloud_api_key:
            headers["Authorization"] = f"Bearer {self._cloud_api_key}"
        return headers

    def _model(self, use_cloud: bool) -> str:
        return self._cloud_model if use_cloud else self._local_model

    def _build_chat_payload(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool,
        stream: bool = False,
        json_mode: bool = False,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "model": self._model(use_cloud),
            "messages": messages,
            "stream": stream,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return payload

    def _prompt_to_messages(self, prompt: str, system: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    # ------------------------------------------------------------------
    # Non-streaming completions
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
        json_mode: bool = False,
    ) -> str:
        """Return a single completion for ``prompt``."""
        messages = self._prompt_to_messages(prompt, system)
        return await self.generate_chat(messages, use_cloud=use_cloud, json_mode=json_mode)

    async def generate_chat(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
        json_mode: bool = False,
    ) -> str:
        """Return one completion given a chat history."""
        payload = self._build_chat_payload(messages, use_cloud, stream=False, json_mode=json_mode)
        url = self._chat_url(use_cloud)

        try:
            resp = await self._client.post(url, json=payload, headers=self._headers(use_cloud))
            resp.raise_for_status()
            data = resp.json()
            return typing.cast(str, data["choices"][0]["message"]["content"])
        except httpx.HTTPStatusError as exc:
            logger.error("[LLM] HTTP error %s — %s", exc.response.status_code, exc.response.text[:200])
            raise
        except Exception as exc:
            logger.error("[LLM] generate_chat failed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Streaming completions
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens for ``prompt`` (real-time TTS pipelines)."""
        messages = self._prompt_to_messages(prompt, system)
        async for token in self.generate_chat_stream(messages, use_cloud=use_cloud):
            yield token

    async def generate_chat_stream(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed token deltas given a chat history.

        Iterates over Server-Sent Events (SSE) lines. Each ``data:`` line
        contains a JSON chunk with a ``choices[0].delta.content`` field.
        The sentinel ``data: [DONE]`` ends the stream.
        """
        payload = self._build_chat_payload(messages, use_cloud, stream=True)
        url = self._chat_url(use_cloud)

        try:
            async with self._client.stream(
                "POST", url, json=payload, headers=self._headers(use_cloud)
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        chunk = json.loads(raw)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except httpx.HTTPStatusError as exc:
            logger.error("[LLM] Stream HTTP error %s — %s", exc.response.status_code, exc.response.text[:200])
            raise
        except Exception as exc:
            logger.error("[LLM] generate_chat_stream failed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    async def embed(self, text: str, use_cloud: bool = False) -> list[float]:
        """Return a float vector embedding for ``text``.

        Local path  → Ollama  ``POST {base}/api/embeddings``
                      body: ``{"model": ..., "prompt": text}``
        Cloud path  → OpenAI-compatible ``POST {base}/v1/embeddings``
                      body: ``{"model": ..., "input": text}``

        Returns an empty list if the endpoint is unavailable or returns
        an unexpected shape, so callers should handle ``[]`` gracefully.
        """
        if use_cloud and self._cloud_api_key:
            return await self._embed_openai(text)
        return await self._embed_ollama(text)

    async def _embed_ollama(self, text: str) -> list[float]:
        """Call Ollama's /api/embeddings endpoint."""
        url = f"{self._local_base_url}/api/embeddings"
        payload = {"model": self._local_model, "prompt": text}
        try:
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            embedding: list[float] = data.get("embedding", [])
            return embedding
        except Exception as exc:
            logger.error("[LLM] embed_ollama failed: %s", exc)
            return []

    async def _embed_openai(self, text: str) -> list[float]:
        """Call OpenAI-compatible /v1/embeddings endpoint."""
        url = f"{self._cloud_base_url}/v1/embeddings"
        payload = {"model": self._cloud_model, "input": text}
        headers = self._headers(use_cloud=True)
        try:
            resp = await self._client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            embedding: list[float] = data["data"][0]["embedding"]
            return embedding
        except Exception as exc:
            logger.error("[LLM] embed_openai failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Release the underlying HTTP client."""
        await self._client.aclose()
