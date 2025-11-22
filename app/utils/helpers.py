import json
import hashlib
import re
from typing import Dict, Any, Optional
from loguru import logger


def calculate_content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    if not response_text:
        logger.warning("Empty response text")
        return None

    response_text = response_text.strip()

    # Try each parsing strategy in order
    for parser in (
        _try_direct_parse,
        _try_code_block,
        _try_bracket_extract,
        _try_remove_prefix,
    ):
        result = parser(response_text)
        if result is not None:
            return result

    logger.error(f"Failed to parse JSON from response. First 200 chars: {response_text[:200]}")
    return None


def _try_direct_parse(text: str) -> Optional[Dict[str, Any]]:
    """Try plain JSON parsing."""
    try:
        return json.loads(text)
    except Exception:
        return None


def _try_code_block(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON inside Markdown code fences:

    ```json
    { ... }
    ```

    or

    ```
    { ... }
    ```
    """
    patterns = [
        r"```json\s*(\{.*?\})\s*```",
        r"```\s*(\{.*?\})\s*```",
        r"```json\s*(\[.*?\])\s*```",
        r"```\s*(\[.*?\])\s*```",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except Exception:
                continue

    return None


def _try_bracket_extract(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON by locating the first {...} or [...]."""
    # Try object
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except Exception:
            pass

    # Try array
    start_idx = text.find('[')
    end_idx = text.rfind(']')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except Exception:
            pass

    return None


def _try_remove_prefix(text: str) -> Optional[Dict[str, Any]]:
    prefixes_to_remove = [
        "Here is the JSON:",
        "Here's the JSON:",
        "JSON response:",
        "Response:",
        "Output:",
        "Result:"
    ]
    for prefix in prefixes_to_remove:
        if text.lower().startswith(prefix.lower()):
            cleaned = text[len(prefix):].strip()
            try:
                return json.loads(cleaned)
            except Exception:
                pass
    return None


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
