"""Crossref ingestion helpers."""
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
BASE_URL = "https://api.crossref.org/works"
DEFAULT_ROWS = 100


def fetch_crossref(query: str, rows: int = DEFAULT_ROWS) -> List[Record]:
    params = {"query": query, "rows": rows}
    mailto = os.getenv("CROSSREF_MAILTO")
    headers = {"User-Agent": f"MethodShift/0.1 (mailto:{mailto})" if mailto else "MethodShift/0.1"}
    with httpx.Client(timeout=30.0, headers=headers) as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    items = data.get("message", {}).get("items", [])
    records: List[Record] = []
    for item in items:
        doi = item.get("DOI")
        year = None
        if "published-print" in item:
            year = item["published-print"].get("date-parts", [[None]])[0][0]
        elif "published-online" in item:
            year = item["published-online"].get("date-parts", [[None]])[0][0]
        authors = [
            clean_text(" ".join(filter(None, [a.get("given"), a.get("family")]))).strip()
            for a in item.get("author", [])
        ]
        record = Record(
            id=f"doi:{doi}" if doi else f"crossref:{item.get('URL')}",
            source="crossref",
            title=clean_text(" ".join(item.get("title", []))),
            abstract=None,
            year=int(year) if isinstance(year, int) else None,
            venue=item.get("container-title", [None])[0],
            fields=item.get("subject", []) or [],
            authors=[a for a in authors if a],
            doi=doi,
            arxiv_id=None,
            language=item.get("language"),
        )
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Crossref metadata")
    parser.add_argument("--query", required=True)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--out", default="data/raw/crossref.parquet")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_crossref(args.query, rows=args.rows)
    df = pd.DataFrame([record.to_dict() for record in records])
    df.to_parquet(args.out)
    LOGGER.info("Saved %s Crossref records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
