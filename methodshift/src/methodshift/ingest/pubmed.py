"""Minimal PubMed ingestion helpers."""
from __future__ import annotations

import argparse
import logging
import os
import xml.etree.ElementTree as ET
from typing import Iterable, List

import httpx
import pandas as pd

from methodshift.utils.schema import Record
from methodshift.utils.text import clean_text

LOGGER = logging.getLogger(__name__)
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DEFAULT_RETMAX = 200


def _client() -> httpx.Client:
    headers = {"User-Agent": "MethodShift/0.1"}
    return httpx.Client(timeout=30.0, headers=headers)


def ids_for_term(term: str, mindate: int = 2000, maxdate: int = 2025, retmax: int = DEFAULT_RETMAX) -> List[str]:
    """Retrieve PubMed IDs for a search term."""
    params = {
        "db": "pubmed",
        "term": term,
        "mindate": mindate,
        "maxdate": maxdate,
        "retmode": "json",
        "retmax": retmax,
    }
    email = os.getenv("ENTREZ_EMAIL")
    if email:
        params["email"] = email
    with _client() as client:
        response = client.get(ESEARCH, params=params)
        response.raise_for_status()
        return response.json()["esearchresult"].get("idlist", [])


def fetch_details(pmids: Iterable[str]) -> List[Record]:
    pmid_list = list(pmids)
    if not pmid_list:
        return []
    params = {"db": "pubmed", "id": ",".join(pmid_list), "retmode": "xml"}
    email = os.getenv("ENTREZ_EMAIL")
    if email:
        params["email"] = email
    with _client() as client:
        response = client.get(EFETCH, params=params)
        response.raise_for_status()
    root = ET.fromstring(response.text)
    records: List[Record] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        article_title = clean_text(article.findtext(".//ArticleTitle"))
        abstract_text = " ".join(
            clean_text(elem.text) for elem in article.findall(".//AbstractText") if elem.text
        ) or None
        year_text = article.findtext(".//JournalIssue/PubDate/Year")
        record = Record(
            id=f"pubmed:{pmid}",
            source="pubmed",
            title=article_title,
            abstract=abstract_text,
            year=int(year_text) if year_text and year_text.isdigit() else None,
            venue=article.findtext(".//Journal/Title"),
            fields=[mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName") if mesh.text],
            authors=[clean_text(a.findtext("LastName") or "") for a in article.findall(".//Author") if a.findtext("LastName")],
            doi=article.findtext(".//ArticleId[@IdType='doi']"),
            arxiv_id=None,
            language=article.findtext(".//Language"),
        )
        records.append(record)
    return records


def fetch_pubmed(term: str, retmax: int = DEFAULT_RETMAX) -> List[Record]:
    """Fetch PubMed records for a search term."""
    pmids = ids_for_term(term, retmax=retmax)
    return fetch_details(pmids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch PubMed abstracts")
    parser.add_argument("--term", required=True)
    parser.add_argument("--retmax", type=int, default=DEFAULT_RETMAX)
    parser.add_argument("--out", default="data/raw/pubmed.parquet")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    records = fetch_pubmed(args.term, retmax=args.retmax)
    df = pd.DataFrame([record.to_dict() for record in records])
    df.to_parquet(args.out)
    LOGGER.info("Saved %s PubMed records to %s", len(df), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
