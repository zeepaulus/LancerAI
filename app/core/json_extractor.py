"""Robust JSON extraction and parsing utilities for LLM responses.

Handles common LLM output quirks:
  - Markdown code fences (```json ... ```)
  - <think>...</think> tags (NVIDIA NIM thinking mode)
  - Trailing commas in objects/arrays
  - Single-quoted strings → double-quoted
  - Conversational text before/after the JSON block
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Pre-compiled patterns
_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_TRAILING_COMMA_RE = re.compile(r",\s*([\]}])")
_SINGLE_QUOTE_KEY_RE = re.compile(r"'(\w+)'\s*:")


def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks produced by models with enable_thinking."""
    return _THINK_TAG_RE.sub("", text).strip()


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ] — a common LLM JSON error."""
    return _TRAILING_COMMA_RE.sub(r"\1", text)


def _fix_single_quote_keys(text: str) -> str:
    """Convert single-quoted keys to double-quoted: 'key': → "key":"""
    return _SINGLE_QUOTE_KEY_RE.sub(r'"\1":', text)


def _fix_newlines_in_strings(text: str) -> str:
    """Replace literal newlines inside JSON string values with \\n."""
    # Only operate on text that looks like JSON
    result: list[str] = []
    in_string = False
    escape = False
    for char in text:
        if escape:
            result.append(char)
            escape = False
            continue
        if char == "\\":
            escape = True
            result.append(char)
            continue
        if char == '"':
            in_string = not in_string
            result.append(char)
            continue
        if in_string and char == "\n":
            result.append("\\n")
            continue
        result.append(char)
    return "".join(result)


def extract_json_str(text: str) -> str:
    """Extract a JSON substring from text that might contain markdown fences,
    think tags, or conversational prefixes/suffixes."""
    # 1. Strip think tags first
    text = _strip_think_tags(text).strip()

    # 2. Look for ```json ... ``` block
    if "```json" in text:
        try:
            parts = text.split("```json")
            if len(parts) > 1:
                sub = parts[1].split("```")[0].strip()
                if sub:
                    return sub
        except Exception:
            pass

    # 3. Look for general ``` ... ``` block
    if "```" in text:
        try:
            parts = text.split("```")
            if len(parts) > 2:
                content = parts[1].strip()
                lines = content.split("\n")
                if lines and lines[0].strip().lower() in ("json", "javascript", "python", ""):
                    content = "\n".join(lines[1:]).strip()
                if content:
                    return content
        except Exception:
            pass

    # 4. Find first brace { or bracket [ and last matching brace/bracket
    first_brace = text.find("{")
    first_bracket = text.find("[")

    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        last_brace = text.rfind("}")
        if last_brace != -1:
            return text[first_brace:last_brace + 1]
    elif first_bracket != -1:
        last_bracket = text.rfind("]")
        if last_bracket != -1:
            return text[first_bracket:last_bracket + 1]

    return text


def clean_and_parse_json(text: str) -> Any:
    """Robustly extract and parse JSON from LLM outputs.

    Strategy (ordered from fastest to most aggressive):
      1. Extract JSON substring from markdown/text wrappers.
      2. Try standard json.loads.
      3. Fix trailing commas + single-quoted keys + newlines, retry.
      4. Fall back to raw text parse as last resort.
    """
    extracted = extract_json_str(text)

    # Attempt 1: direct parse
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        pass

    # Attempt 2: fix common issues
    fixed = extracted
    fixed = _fix_trailing_commas(fixed)
    fixed = _fix_single_quote_keys(fixed)
    fixed = _fix_newlines_in_strings(fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        logger.warning(
            "JSON parsing failed after fixes. Error: %s. Text sample: %r",
            e,
            fixed[:300],
        )

    # Attempt 3: raw text as last resort
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    raise json.JSONDecodeError(
        "Could not extract valid JSON from LLM response",
        text[:200],
        0,
    )
