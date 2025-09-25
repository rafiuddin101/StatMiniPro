"""Tests for schema validation and deduplication."""
from __future__ import annotations

import pandas as pd

from methodshift.utils.dedupe import deduplicate_records
from methodshift.utils.schema import Record, validate_dataframe
from methodshift.utils.text import fingerprint_title


def test_record_validation_roundtrip() -> None:
    record = Record(
        id="doi:10.1234/example",
        source="crossref",
        title="An Example Paper",
        abstract="We explore example-driven science.",
        year=2020,
        venue="Journal of Examples",
        fields=["Statistics", "Machine Learning"],
        authors=["Doe, Jane", "Smith, John"],
        doi="10.1234/example",
        arxiv_id=None,
        language="en",
    )
    df = validate_dataframe(pd.DataFrame([record.to_dict()]))
    assert df.iloc[0]["title"] == "An Example Paper"
    assert df.iloc[0]["authors"] == ["Doe, Jane", "Smith, John"]


def test_deduplicate_records_prefers_priority_source() -> None:
    df = pd.DataFrame(
        [
            {
                "id": "doi:10.1/abc",
                "source": "openalex",
                "title": "Bayesian methods in ecology",
                "abstract": "",
                "year": 2021,
                "venue": "",
                "fields": [],
                "authors": ["A"],
                "doi": "10.1/abc",
                "arxiv_id": None,
                "language": "en",
            },
            {
                "id": "doi:10.1/abc",
                "source": "crossref",
                "title": "Bayesian methods in ecology",
                "abstract": "",
                "year": 2021,
                "venue": "",
                "fields": [],
                "authors": ["A"],
                "doi": "10.1/abc",
                "arxiv_id": None,
                "language": "en",
            },
        ]
    )
    deduped, stats = deduplicate_records(df)
    assert len(deduped) == 1
    assert stats.unique == 1
    assert deduped.iloc[0]["source"] == "crossref"


def test_title_fingerprint_stability() -> None:
    title = "Bayesian Inference for Logistic Regression"
    fp1 = fingerprint_title(title)
    fp2 = fingerprint_title(title.lower())
    assert fp1 == fp2
    assert fp1.split()[0] == "bayesian"
