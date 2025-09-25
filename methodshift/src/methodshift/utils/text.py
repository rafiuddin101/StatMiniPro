"""Text processing helpers."""
from __future__ import annotations

import re
from typing import Iterable, List

TOKEN_PATTERN = re.compile(r"[\w']+")


def clean_text(text: str | None) -> str:
    """Normalize whitespace and strip control characters."""
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


def fingerprint_title(title: str, max_tokens: int = 12) -> str:
    """Generate a lightweight title fingerprint for deduplication."""
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(title)]
    return " ".join(tokens[:max_tokens])


def tokenize(text: str) -> List[str]:
    """Tokenize a string into lowercase tokens."""
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def ngrams(tokens: Iterable[str], n: int = 2) -> List[str]:
    """Generate n-grams from a token list."""
    sequence = list(tokens)
    return [" ".join(sequence[i : i + n]) for i in range(len(sequence) - n + 1)]


__all__ = ["clean_text", "fingerprint_title", "tokenize", "ngrams"]
