"""Utilities for downloading metadata from the arXiv API."""
from __future__ import annotations

import argparse
import logging
import time
from typing import Iterable, List

import httpx
import pandas as pd

from methodshift.utils.schema import Record
from methodshift.utils.text import clean_text

LOGGER = logging.getLogger(__name__)
BASE_URL = "http://export.arxiv.org/api/query"
DEFAULT_PAGE_SIZE = 100


def build_params(
    query: str,
    start: int = 0,
    page_size: int = DEFAULT_PAGE_SIZE,
    sort_by: str = "submittedDate",
    sort_order: str = "ascending",
) -> dict[str, str | int]:
    """Construct the API query parameters."""
    return {
        "search_query": query,
        "start": start,
        "max_results": page_size,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }


def fetch_page(client: httpx.Client, params: dict[str, str | int]) -> httpx.Response:
    """Fetch a single page with retry logic."""
    backoff = 1.0
    for attempt in range(5):
        try:
            LOGGER.debug("Fetching arXiv page with params=%s", params)
            response = client.get(BASE_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:  # pragma: no cover - network failure guard
            LOGGER.warning("arXiv request failed on attempt %s: %s", attempt + 1, exc)
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError("Failed to fetch arXiv data after multiple retries")


def parse_feed(feed_text: str) -> List[Record]:
    """Parse the Atom feed into validated records."""
    # feedparser is not part of the runtime dependencies; to keep the scaffold
    # lightweight we implement minimal parsing using pandas.read_xml when
    # available. The function is resilient to missing optional fields.
    df = pd.read_xml(feed_text, xpath="//entry")
    if df is None or df.empty:
        return []
    records: List[Record] = []
    for _, row in df.iterrows():
        arxiv_id = str(row.get("id", "")).split("/")[-1]
        summary = clean_text(row.get("summary", ""))
        record = Record(
            id=f"arxiv:{arxiv_id}",
            source="arxiv",
            title=clean_text(row.get("title", "")),
            abstract=summary or None,
            year=int(str(row.get("published", ""))[:4] or 0) or None,
            venue="arXiv",
            fields=[],
            authors=[a.strip() for a in str(row.get("author", "")).split(":") if a],
            doi=row.get("doi"),
            arxiv_id=arxiv_id or None,
            language="en",
        )
        records.append(record)
    return records


def fetch_arxiv(
    query: str,
    max_results: int = 100,
    page_size: int = DEFAULT_PAGE_SIZE,
    delay: float = 3.0,
) -> List[Record]:
    """Fetch records from arXiv for a given query.

    The function respects a polite delay between requests and returns validated
    :class:`Record` objects ready for downstream use.
    """
    fetched: List[Record] = []
    with httpx.Client(headers={"User-Agent": "MethodShift/0.1"}) as client:
        start = 0
        while len(fetched) < max_results:
            params = build_params(query=query, start=start, page_size=page_size)
            response = fetch_page(client, params)
            new_records = parse_feed(response.text)
            if not new_records:
                break
            fetched.extend(new_records)
            if len(new_records) < page_size:
                break
            start += page_size
            time.sleep(delay)
    return fetched[:max_results]


def records_to_dataframe(records: Iterable[Record]) -> pd.DataFrame:
    """Convert validated records into a pandas DataFrame."""
    return pd.DataFrame([r.to_dict() for r in records])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch arXiv metadata")
    parser.add_argument("--query", required=True, help="arXiv search query")
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument(
        "--out",
        type=str,
        default="data/raw/arxiv.parquet",
        help="Output parquet path",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_arxiv(args.query, max_results=args.max_results, page_size=args.page_size)
    df = records_to_dataframe(records)
    if df.empty:
        LOGGER.warning("No records returned for query '%s'", args.query)
    df.to_parquet(args.out)
    LOGGER.info("Saved %s records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
