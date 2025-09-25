"""Semantic Scholar ingestion helpers."""
from __future__ import annotations

import argparse
import logging
import os
from typing import List

import httpx
import pandas as pd

from methodshift.utils.schema import Record
from methodshift.utils.text import clean_text

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
DEFAULT_LIMIT = 100
FIELDS = "paperId,title,abstract,year,venue,authors,externalIds,fieldsOfStudy,publicationTypes,publicationDate"


def fetch_semantic_scholar(query: str, limit: int = DEFAULT_LIMIT) -> List[Record]:
    headers = {"User-Agent": "MethodShift/0.1"}
    api_key = os.getenv("S2_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    params = {"query": query, "limit": limit, "fields": FIELDS}
    with httpx.Client(timeout=30.0, headers=headers) as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    records: List[Record] = []
    for item in data.get("data", []):
        external = item.get("externalIds", {})
        record = Record(
            id=f"s2:{item.get('paperId')}",
            source="s2",
            title=clean_text(item.get("title", "")),
            abstract=clean_text(item.get("abstract", "")) or None,
            year=item.get("year"),
            venue=item.get("venue"),
            fields=item.get("fieldsOfStudy", []) or [],
            authors=[author.get("name") for author in item.get("authors", []) if author.get("name")],
            doi=external.get("DOI"),
            arxiv_id=external.get("ArXiv"),
            language=None,
        )
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Semantic Scholar metadata")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--out", default="data/raw/semanticscholar.parquet")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_semantic_scholar(args.query, limit=args.limit)
    df = pd.DataFrame([record.to_dict() for record in records])
    df.to_parquet(args.out)
    LOGGER.info("Saved %s Semantic Scholar records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
