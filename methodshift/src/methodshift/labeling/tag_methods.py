"""Dictionary-based method tagging."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd
import yaml

from methodshift.utils.schema import validate_dataframe
from methodshift.utils.text import clean_text

LOGGER = logging.getLogger(__name__)


def load_dictionary(path: str | Path) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return {key: [phrase.lower() for phrase in phrases] for key, phrases in raw.items()}


def tag_text(text: str, dictionary: Dict[str, List[str]]) -> Set[str]:
    text_lower = text.lower()
    hits = {method for method, phrases in dictionary.items() if any(phrase in text_lower for phrase in phrases)}
    return hits


def tag_records(df: pd.DataFrame, dictionary: Dict[str, List[str]]) -> pd.DataFrame:
    df = validate_dataframe(df)
    tags: List[Set[str]] = []
    for row in df.itertuples(index=False):
        corpus = " ".join(filter(None, [row.title, row.abstract or ""]))
        hits = tag_text(clean_text(corpus), dictionary)
        tags.append(hits)
    tagged = df.copy()
    tagged["methods"] = [sorted(list(hit_set)) for hit_set in tags]
    return tagged


def main() -> None:
    parser = argparse.ArgumentParser(description="Tag records with statistical methods")
    parser.add_argument("--input", required=True, help="Input parquet file")
    parser.add_argument("--dictionary", default=Path(__file__).with_name("method_dict.yaml"))
    parser.add_argument("--out", required=True, help="Output parquet file")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    dictionary = load_dictionary(args.dictionary)
    df = pd.read_parquet(args.input)
    tagged = tag_records(df, dictionary)
    tagged.to_parquet(args.out)
    LOGGER.info("Tagged %s records and saved to %s", len(tagged), args.out)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
