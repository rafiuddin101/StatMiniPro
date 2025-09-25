"""Unified schema definitions and helpers for MethodShift."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping

import pandas as pd


def _normalize_list(values: Iterable[str]) -> List[str]:
    seen = set()
    cleaned: List[str] = []
    for value in values:
        if value is None:
            continue
        token = str(value).strip()
        if token and token not in seen:
            cleaned.append(token)
            seen.add(token)
    return cleaned


def _maybe_str(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _maybe_int(value: object | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid integer value: {value}") from exc


@dataclass
class Record:
    """Canonical representation of a single scholarly record."""

    id: str
    source: str
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    fields: List[str] = field(default_factory=list)
    authors: List[str] = field(default_factory=list)
    doi: str | None = None
    arxiv_id: str | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        self.id = self.id.strip()
        self.source = self.source.strip()
        self.title = self.title.strip()
        self.fields = _normalize_list(self.fields)
        self.authors = _normalize_list(self.authors)
        if self.year is not None:
            self.year = int(self.year)
            if not 1800 <= self.year <= 2100:
                raise ValueError(f"Year {self.year} is outside expected bounds")

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, object]) -> "Record":
        return cls(
            id=str(mapping.get("id", "")),
            source=str(mapping.get("source", "")),
            title=str(mapping.get("title", "")),
            abstract=_maybe_str(mapping.get("abstract")),
            year=_maybe_int(mapping.get("year")),
            venue=_maybe_str(mapping.get("venue")),
            fields=list(mapping.get("fields", []) or []),
            authors=list(mapping.get("authors", []) or []),
            doi=_maybe_str(mapping.get("doi")),
            arxiv_id=_maybe_str(mapping.get("arxiv_id")),
            language=_maybe_str(mapping.get("language")),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def dataframe_from_records(records: Iterable[Record]) -> pd.DataFrame:
    return pd.DataFrame([record.to_dict() for record in records])


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    records = [Record.from_mapping(row) for row in df.to_dict(orient="records")]
    return dataframe_from_records(records)


def save_records(records: Iterable[Record], path: str | Path) -> None:
    dataframe_from_records(records).to_parquet(path)


def load_records(path: str | Path) -> List[Record]:
    df = pd.read_parquet(path)
    return [Record.from_mapping(row) for row in df.to_dict(orient="records")]


__all__ = ["Record", "dataframe_from_records", "validate_dataframe", "save_records", "load_records"]
