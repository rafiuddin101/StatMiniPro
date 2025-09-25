"""OpenAlex ingestion helpers."""
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
BASE_URL = "https://api.openalex.org/works"
DEFAULT_PER_PAGE = 200
DEFAULT_PAGES = 3


def fetch_openalex(
    query: str,
    per_page: int = DEFAULT_PER_PAGE,
    pages: int = DEFAULT_PAGES,
) -> List[Record]:
    params = {"search": query, "per_page": per_page, "cursor": "*"}
    email = os.getenv("OPENALEX_EMAIL")
    if email:
        params["mailto"] = email
    records: List[Record] = []
    with httpx.Client(timeout=30.0, headers={"User-Agent": "MethodShift/0.1"}) as client:
        for _ in range(pages):
            response = client.get(BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            for work in payload.get("results", []):
                abstract = None
                inverted = work.get("abstract_inverted_index")
                if inverted:
                    tokens = sorted(
                        ((pos, word) for word, positions in inverted.items() for pos in positions),
                        key=lambda item: item[0],
                    )
                    abstract = " ".join(word for _, word in tokens)
                record = Record(
                    id=work["id"],
                    source="openalex",
                    title=clean_text(work.get("title", "")),
                    abstract=abstract,
                    year=work.get("publication_year"),
                    venue=(work.get("host_venue") or {}).get("display_name"),
                    fields=[c.get("display_name") for c in work.get("concepts", []) if c.get("display_name")],
                    authors=[a["author"].get("display_name") for a in work.get("authorships", []) if a.get("author")],
                    doi=work.get("doi"),
                    arxiv_id=None,
                    language=work.get("language"),
                )
                records.append(record)
            cursor = payload.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            params["cursor"] = cursor
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch OpenAlex works")
    parser.add_argument("--query", required=True)
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    parser.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    parser.add_argument("--out", default="data/raw/openalex.parquet")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_openalex(args.query, per_page=args.per_page, pages=args.pages)
    df = pd.DataFrame([record.to_dict() for record in records])
    df.to_parquet(args.out)
    LOGGER.info("Saved %s OpenAlex records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
