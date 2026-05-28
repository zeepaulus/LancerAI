"""LLM Connector — unified interface for Local + Cloud LLMs.

Strategy:
    - Local: Ollama (OpenAI-compatible /v1/chat/completions endpoint).
    - Cloud Groq: OpenAI-compatible for heavier reasoning tasks (fallback).
    - Cloud NVIDIA NIM: Primary cloud backend — supports ``google/gemma-4-31b-it``
      and other NVIDIA-hosted models with ``enable_thinking`` for chain-of-thought.

All three paths use the OpenAI chat format. The ``use_cloud`` / ``use_nvidia``
flags select which base URL and API key are used for each call.

Streaming is implemented via Server-Sent Events (SSE) iteration with
``httpx.AsyncClient.stream``, yielding text deltas token by token.

Semantic Cache:
    ``generate`` and ``generate_chat`` accept an optional ``cache_repo``
    (``LLMCacheRepository``) and ``user_id``. When provided:
      1. SHA-256 exact lookup (O(1) fast path).
      2. Cosine similarity scan if exact lookup misses.
      3. On cache MISS — call LLM, embed prompt, persist response.
"""

from __future__ import annotations

import json
import logging
import typing
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import httpx

from app.models.llm_cache import LLMResponseCache

if TYPE_CHECKING:
    from app.repository.llm_cache_repository import LLMCacheRepository

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(connect=10.0, read=600.0, write=30.0, pool=10.0)

# Backend name constants
BACKEND_OLLAMA = "ollama"
BACKEND_GROQ = "groq"
BACKEND_NVIDIA = "nvidia"


class LLMConnector:
    """Single entry point used by every service that needs an LLM."""

    def __init__(
        self,
        local_base_url: str,
        local_model: str,
        cloud_base_url: str,
        cloud_api_key: str,
        cloud_model: str,
        # NVIDIA NIM configuration
        nvidia_base_url: str = "https://integrate.api.nvidia.com",
        nvidia_api_key: str = "",
        nvidia_model: str = "google/gemma-4-31b-it",
        nvidia_max_tokens: int = 16384,
        nvidia_enable_thinking: bool = True,
    ) -> None:
        self._local_base_url = local_base_url.rstrip("/")
        self._local_model = local_model
        self._cloud_base_url = cloud_base_url.rstrip("/")
        self._cloud_api_key = cloud_api_key
        self._cloud_model = cloud_model

        self._nvidia_base_url = nvidia_base_url.rstrip("/")
        self._nvidia_api_key = nvidia_api_key
        self._nvidia_model = nvidia_model
        self._nvidia_max_tokens = nvidia_max_tokens
        self._nvidia_enable_thinking = nvidia_enable_thinking

        self._client = httpx.AsyncClient(timeout=_TIMEOUT)

    def _resolve_nvidia(self, use_cloud: bool, use_nvidia: bool) -> tuple[bool, bool]:
        """Auto-promote to NVIDIA if nvidia key is set and cloud key is empty/placeholder."""
        if use_nvidia:
            return False, True
        
        is_placeholder_cloud = not self._cloud_api_key or "your-groq" in self._cloud_api_key
        has_nvidia = bool(self._nvidia_api_key) and "your-nvidia" not in self._nvidia_api_key
        
        if (use_cloud or is_placeholder_cloud) and has_nvidia:
            return False, True
            
        return use_cloud, use_nvidia

    def _chat_url(self, use_cloud: bool, use_nvidia: bool = False) -> str:
        if use_nvidia:
            return f"{self._nvidia_base_url}/v1/chat/completions"
        base = self._cloud_base_url if use_cloud else self._local_base_url
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def _headers(self, use_cloud: bool, use_nvidia: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if use_nvidia and self._nvidia_api_key:
            headers["Authorization"] = f"Bearer {self._nvidia_api_key}"
        elif use_cloud and self._cloud_api_key:
            headers["Authorization"] = f"Bearer {self._cloud_api_key}"
        return headers

    def _model(self, use_cloud: bool, use_nvidia: bool = False) -> str:
        if use_nvidia:
            return self._nvidia_model
        return self._cloud_model if use_cloud else self._local_model

    def _backend_name(self, use_cloud: bool, use_nvidia: bool = False) -> str:
        if use_nvidia:
            return BACKEND_NVIDIA
        return BACKEND_GROQ if use_cloud else BACKEND_OLLAMA

    def _build_chat_payload(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool,
        use_nvidia: bool = False,
        stream: bool = False,
        json_mode: bool = False,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "model": self._model(use_cloud, use_nvidia),
            "messages": messages,
            "stream": stream,
        }
        if json_mode and not use_nvidia:
            payload["response_format"] = {"type": "json_object"}
        if use_nvidia:
            payload["max_tokens"] = self._nvidia_max_tokens
            payload["temperature"] = 1.0
            payload["top_p"] = 0.95
            if self._nvidia_enable_thinking:
                payload["chat_template_kwargs"] = {"enable_thinking": True}
        return payload

    def _prompt_to_messages(self, prompt: str, system: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _full_prompt_str(self, messages: list[dict[str, str]]) -> str:
        """Serialise messages to a canonical string for hashing and embedding."""
        return "\n".join(f"[{m['role']}] {m['content']}" for m in messages)

    # ------------------------------------------------------------------
    # Non-streaming completions
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
        use_nvidia: bool = False,
        json_mode: bool = False,
        # Cache integration
        cache_repo: LLMCacheRepository | None = None,
        cache_threshold: float = 0.92,
        user_id: str | None = None,
    ) -> str:
        """Return a single completion for ``prompt``."""
        messages = self._prompt_to_messages(prompt, system)
        return await self.generate_chat(
            messages,
            use_cloud=use_cloud,
            use_nvidia=use_nvidia,
            json_mode=json_mode,
            cache_repo=cache_repo,
            cache_threshold=cache_threshold,
            user_id=user_id,
        )

    async def generate_chat(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
        use_nvidia: bool = False,
        json_mode: bool = False,
        # Cache integration
        cache_repo: LLMCacheRepository | None = None,
        cache_threshold: float = 0.92,
        user_id: str | None = None,
    ) -> str:
        use_cloud, use_nvidia = self._resolve_nvidia(use_cloud, use_nvidia)
        model_name = self._model(use_cloud, use_nvidia)
        backend = self._backend_name(use_cloud, use_nvidia)
        prompt_str = self._full_prompt_str(messages)

        # --- Cache lookup ---------------------------------------------------
        if cache_repo is not None:
            cached = await self._cache_lookup(cache_repo, prompt_str, model_name, cache_threshold)
            if cached is not None:
                entry, score = cached
                await cache_repo.increment_hit(entry.id)
                logger.info(
                    "[LLMCache] Serving from cache — score=%.4f model=%s user=%s",
                    score, model_name, user_id,
                )
                return entry.response_text

        # --- LLM call -------------------------------------------------------
        response_text = await self._call_llm(messages, use_cloud, use_nvidia, json_mode)

        # --- Persist to cache -----------------------------------------------
        if cache_repo is not None:
            await self._cache_save(
                cache_repo, prompt_str, response_text, model_name, backend, user_id,
            )

        return response_text

    async def _call_llm(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool,
        use_nvidia: bool,
        json_mode: bool,
    ) -> str:
        payload = self._build_chat_payload(
            messages, use_cloud, use_nvidia, stream=False, json_mode=json_mode
        )
        url = self._chat_url(use_cloud, use_nvidia)
        try:
            resp = await self._client.post(
                url, json=payload, headers=self._headers(use_cloud, use_nvidia)
            )
            resp.raise_for_status()
            data = resp.json()
            return typing.cast(str, data["choices"][0]["message"]["content"])
        except httpx.HTTPStatusError as exc:
            logger.error("[LLM] HTTP error %s — %s", exc.response.status_code, exc.response.text[:200])
            raise
        except Exception as exc:
            logger.exception("[LLM] _call_llm failed")
            raise

    # ------------------------------------------------------------------
    # Cache helpers (internal)
    # ------------------------------------------------------------------

    async def _cache_lookup(
        self,
        cache_repo: LLMCacheRepository,
        prompt_str: str,
        model_name: str,
        threshold: float,
    ) -> tuple[LLMResponseCache, float] | None:
        """Try exact hash first, then vector similarity scan."""
        try:
            # 1. Fast path: exact SHA-256 match
            exact = await cache_repo.find_exact(prompt_str, model_name)
            if exact is not None:
                logger.debug("[LLMCache] Exact hash HIT model=%s", model_name)
                return exact, 1.0

            # 2. Slow path: embed + cosine similarity
            embedding = await self.embed(prompt_str)
            if not embedding:
                return None
            return await cache_repo.find_similar(embedding, model_name, threshold)
        except Exception as exc:
            logger.warning("[LLMCache] Cache lookup error (skipping cache): %s", exc)
            return None

    async def _cache_save(
        self,
        cache_repo: LLMCacheRepository,
        prompt_str: str,
        response_text: str,
        model_name: str,
        backend: str,
        user_id: str | None,
    ) -> None:
        """Embed prompt and persist the cache entry. Errors are non-fatal."""
        try:
            embedding = await self.embed(prompt_str)
            await cache_repo.save(
                prompt_text=prompt_str,
                response_text=response_text,
                prompt_embedding=embedding,
                model_name=model_name,
                backend=backend,
                triggered_by_user_id=user_id,
            )
        except Exception as exc:
            logger.warning("[LLMCache] Cache save error (non-fatal): %s", exc)

    # ------------------------------------------------------------------
    # Streaming completions
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        prompt: str,
        system: str = "",
        use_cloud: bool = False,
        use_nvidia: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed tokens for ``prompt`` (real-time TTS pipelines)."""
        messages = self._prompt_to_messages(prompt, system)
        async for token in self.generate_chat_stream(messages, use_cloud=use_cloud, use_nvidia=use_nvidia):
            yield token

    async def generate_chat_stream(
        self,
        messages: list[dict[str, str]],
        use_cloud: bool = False,
        use_nvidia: bool = False,
    ) -> AsyncGenerator[str, None]:
        use_cloud, use_nvidia = self._resolve_nvidia(use_cloud, use_nvidia)
        payload = self._build_chat_payload(messages, use_cloud, use_nvidia, stream=True)
        url = self._chat_url(use_cloud, use_nvidia)

        try:
            async with self._client.stream(
                "POST", url, json=payload, headers=self._headers(use_cloud, use_nvidia)
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

        Priority:
          1. Local Ollama (offline, free).
          2. NVIDIA NIM embedding endpoint (if Ollama unavailable and NVIDIA key set).
          3. Groq OpenAI-compatible embeddings (last resort).

        Returns an empty list if all endpoints are unavailable.
        """
        # Try Ollama first
        embedding = await self._embed_ollama(text)
        if embedding:
            return embedding

        # Fallback: NVIDIA NIM embedding endpoint
        if self._nvidia_api_key:
            embedding = await self._embed_nvidia(text)
            if embedding:
                return embedding

        # Final fallback: cloud (Groq) OpenAI-compatible
        if use_cloud and self._cloud_api_key:
            return await self._embed_openai(text)

        return []

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
            logger.warning("[LLM] embed_ollama failed (will try fallback): %s", exc)
            return []

    async def _embed_nvidia(self, text: str) -> list[float]:
        """Call NVIDIA NIM /v1/embeddings endpoint."""
        url = f"{self._nvidia_base_url}/v1/embeddings"
        # NVIDIA recommends a dedicated embedding model; fall back to chat model
        payload = {"model": "nvidia/nv-embedqa-e5-v5", "input": text, "input_type": "query"}
        headers = {"Authorization": f"Bearer {self._nvidia_api_key}", "Content-Type": "application/json"}
        try:
            resp = await self._client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            embedding: list[float] = data["data"][0]["embedding"]
            return embedding
        except Exception as exc:
            logger.warning("[LLM] embed_nvidia failed (will try fallback): %s", exc)
            return []

    async def _embed_openai(self, text: str) -> list[float]:
        """Call OpenAI-compatible /v1/embeddings endpoint (Groq fallback)."""
        base = self._cloud_base_url
        if base.endswith("/v1"):
            url = f"{base}/embeddings"
        else:
            url = f"{base}/v1/embeddings"
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
