"""DOAJ ingestion helpers."""
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
BASE_URL = "https://doaj.org/api/v2/search/articles/"
DEFAULT_PAGE_SIZE = 100
DEFAULT_PAGES = 2


def fetch_doaj(query: str, page_size: int = DEFAULT_PAGE_SIZE, pages: int = DEFAULT_PAGES) -> List[Record]:
    headers = {"User-Agent": "MethodShift/0.1"}
    api_key = os.getenv("DOAJ_API_KEY")
    if api_key:
        headers["X-API-KEY"] = api_key
    records: List[Record] = []
    params = {"pageSize": page_size, "page": 1, "q": query}
    with httpx.Client(timeout=30.0, headers=headers) as client:
        for _ in range(pages):
            response = client.get(BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("results", []):
                bibjson = item.get("bibjson", {})
                record = Record(
                    id=item.get("id"),
                    source="doaj",
                    title=clean_text(bibjson.get("title", "")),
                    abstract=clean_text(bibjson.get("abstract", "")) or None,
                    year=int(bibjson.get("year")) if bibjson.get("year") else None,
                    venue=bibjson.get("journal", {}).get("title"),
                    fields=[s.get("term") for s in bibjson.get("subject", []) if s.get("term")],
                    authors=[author.get("name") for author in bibjson.get("author", []) if author.get("name")],
                    doi=bibjson.get("identifier", [{}])[0].get("id") if bibjson.get("identifier") else None,
                    arxiv_id=None,
                    language=bibjson.get("language"),
                )
                records.append(record)
            params["page"] += 1
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch DOAJ articles")
    parser.add_argument("--query", required=True)
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--out", default="data/raw/doaj.parquet")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_doaj(args.query, page_size=args.page_size, pages=args.pages)
    df = pd.DataFrame([record.to_dict() for record in records])
    df.to_parquet(args.out)
    LOGGER.info("Saved %s DOAJ records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
