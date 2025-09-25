"""Deduplication utilities for harmonized records."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List

import pandas as pd

from methodshift.utils.schema import validate_dataframe
from methodshift.utils.text import fingerprint_title

try:  # pragma: no cover - optional dependency
    from rapidfuzz import fuzz

    def similarity_score(a: str, b: str) -> int:
        return int(fuzz.token_set_ratio(a, b))

except ImportError:  # pragma: no cover - fallback path

    def similarity_score(a: str, b: str) -> int:
        def normalize(text: str) -> str:
            tokens = sorted(set(text.split()))
            return " ".join(tokens)

        return int(SequenceMatcher(None, normalize(a), normalize(b)).ratio() * 100)

PRIORITY_ORDER = ["arxiv", "pubmed", "crossref", "openalex", "s2", "doaj"]


@dataclass
class DedupeStats:
    total: int
    unique: int
    merged: int


def _normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    return doi.strip().lower().replace("https://doi.org/", "")


def deduplicate_records(df: pd.DataFrame, similarity_threshold: int = 90) -> tuple[pd.DataFrame, DedupeStats]:
    """Deduplicate records based on DOI, arXiv ID, and fuzzy title fingerprints."""
    if df.empty:
        return df.copy(), DedupeStats(total=0, unique=0, merged=0)

    df = validate_dataframe(df)
    df["doi_norm"] = df["doi"].map(_normalize_doi)
    df["fingerprint"] = df["title"].map(fingerprint_title)

    groups: defaultdict[str, List[int]] = defaultdict(list)

    for idx, row in df.iterrows():
        if row.doi_norm:
            groups[f"doi:{row.doi_norm}"].append(idx)
        elif row.arxiv_id:
            groups[f"arxiv:{row.arxiv_id}"].append(idx)
        else:
            groups[f"fp:{row.fingerprint}"].append(idx)

    selected_rows: List[pd.Series] = []
    merged_count = 0

    for members in groups.values():
        if len(members) == 1:
            selected_rows.append(df.loc[members[0]])
            continue
        primary_idx = sorted(
            members,
            key=lambda i: PRIORITY_ORDER.index(df.at[i, "source"]) if df.at[i, "source"] in PRIORITY_ORDER else len(PRIORITY_ORDER),
        )[0]
        primary = df.loc[primary_idx]
        for idx in members:
            if idx == primary_idx:
                continue
            other = df.loc[idx]
            score = similarity_score(primary["fingerprint"], other["fingerprint"])
            if score >= similarity_threshold:
                merged_count += 1
                continue
            selected_rows.append(other)
        selected_rows.append(primary)

    deduped_df = pd.DataFrame(selected_rows).drop(columns=["doi_norm", "fingerprint"]).reset_index(drop=True)
    return deduped_df, DedupeStats(total=len(df), unique=len(deduped_df), merged=merged_count)


__all__ = ["deduplicate_records", "DedupeStats"]
