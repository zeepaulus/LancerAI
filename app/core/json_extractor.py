"""Robust JSON extraction and parsing utilities for LLM responses."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def extract_json_str(text: str) -> str:
    """Extract a JSON substring from a text that might contain markdown fences or conversational prefixes/suffixes."""
    text = text.strip()
    
    # 1. Look for ```json ... ``` block
    if "```json" in text:
        try:
            parts = text.split("```json")
            if len(parts) > 1:
                sub = parts[1].split("```")[0].strip()
                if sub:
                    return sub
        except Exception:
            pass

    # 2. Look for general ``` ... ``` block
    if "```" in text:
        try:
            parts = text.split("```")
            if len(parts) > 2:
                content = parts[1].strip()
                lines = content.split("\n")
                if lines and lines[0].strip().lower() in ("json", "javascript", "python"):
                    content = "\n".join(lines[1:]).strip()
                if content:
                    return content
        except Exception:
            pass

    # 3. Find first brace { or bracket [ and last matching brace/bracket
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
    """Robustly extract and parse JSON from LLM outputs, falling back to original text if extraction fails."""
    extracted = extract_json_str(text)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError as e:
        logger.warning("JSON parsing failed on extracted content. Error: %s. Extracted text sample: %r", e, extracted[:200])
        # Try raw text as last resort
        return json.loads(text)
