# MethodShift

Quantifying how statistical methods diffuse across research disciplines from 2000–2025 using multi-database open literature metadata.

## Project overview

MethodShift provides a reproducible research pipeline for meta-researchers who want to track how core statistical methods such as logistic regression, Bayesian inference, or causal estimators rise (or decline) in scholarly publishing. The project ingests metadata and abstracts from six major open scholarly databases, harmonizes them into a shared schema, performs fuzzy deduplication, and labels each record with statistical methods using a curated dictionary. The processed data feed hierarchical growth models and changepoint analyses to uncover where and when methods surge, and whether early preprint signals (e.g., arXiv) anticipate adoption in peer-reviewed venues (e.g., PubMed, DOAJ).

This repository contains the scaffolding to launch the study, including modular ingestion scripts, schema validators, labeling utilities, analysis placeholders, and example tests for data validation logic.

## Repository layout

```
methodshift/
├─ README.md
├─ LICENSE
├─ pyproject.toml
├─ src/
│  └─ methodshift/
│     ├─ __init__.py
│     ├─ ingest/
│     ├─ utils/
│     ├─ labeling/
│     ├─ analysis/
│     └─ viz/
├─ data/
│  ├─ raw/
│  ├─ interim/
│  └─ processed/
├─ notebooks/
├─ tests/
└─ .github/workflows/
```

### Key components

* **Ingestion modules** (`src/methodshift/ingest/`): Thin wrappers around the public APIs for arXiv, PubMed, Crossref, OpenAlex, Semantic Scholar, and DOAJ with respect for rate limits and reproducibility via query logging.
* **Schema utilities** (`src/methodshift/utils/schema.py`): Define the unified record dataclass with lightweight validation helpers for reading and writing parquet files.
* **Deduplication utilities** (`src/methodshift/utils/dedupe.py`): Combine DOI, arXiv IDs, and fuzzy title fingerprints (with RapidFuzz or a difflib fallback) to collapse duplicate records from different sources.
* **Labeling tools** (`src/methodshift/labeling/`): Curated dictionary (`method_dict.yaml`) and tagging script to annotate abstracts/titles with statistical method mentions.
* **Analysis templates** (`src/methodshift/analysis/`): Functions to build method × field × year tables, run Poisson/Negative Binomial regressions, and detect changepoints.
* **Visualization helpers** (`src/methodshift/viz/plots.py`): Convenience functions to create publication-quality figures summarizing adoption trends.

## Getting started

### Prerequisites

* Python 3.11+
* Recommended: [uv](https://github.com/astral-sh/uv) or `pip` for dependency management.

### Setup

```bash
# Create and activate a virtual environment
uv venv && source .venv/bin/activate  # or python -m venv .venv && source .venv/bin/activate

# Install dependencies
uv pip install .  # or: pip install -e .

# Configure API credentials (if available)
cp .env.example .env
# Then edit .env with values such as:
# OPENALEX_EMAIL=you@example.com
# ENTREZ_EMAIL=you@example.com
# S2_API_KEY=...  # Semantic Scholar Graph API (optional)
```

### Data pipeline

1. **Ingest** metadata from each source. Each module exposes both a `fetch_*` helper and a CLI entry point for batch downloads. Results are saved as parquet or ndjson files under `data/raw/<source>/`.
2. **Harmonize** raw tables into the unified schema by loading them into pandas and running `methodshift.utils.schema.validate_dataframe`.
3. **Deduplicate** merged tables with `methodshift.utils.dedupe.deduplicate_records`, preferring richer metadata.
4. **Label methods** using `python -m methodshift.labeling.tag_methods --input data/interim/merged.parquet --out data/processed/labeled.parquet`.
5. **Analyze trends** with the modeling utilities in `src/methodshift/analysis/` and create visuals with `src/methodshift/viz/plots.py`.

Each CLI step logs parameters and timestamps so the study is reproducible.

## Development

* Run `pytest` to execute the schema and dedupe tests.
* `ruff` and `mypy` configurations can be added later; the scaffold keeps dependencies minimal.
* Use `.env` for credentials; the project reads configuration via environment variables to avoid hard-coding secrets.

## Research questions

1. Which statistical methods are growing or declining fastest by field and year?
2. Do method adoption curves differ by database (arXiv vs PubMed vs DOAJ/OpenAlex/Semantic Scholar/Crossref)?
3. When do changepoints occur, and are they synchronized across fields or sources?
4. Are early arXiv signals predictive of later PubMed or DOAJ adoption?

## Ethics

* Respect API rate limits and terms of service.
* Store only metadata and abstracts permitted by the source.
* Provide attribution when using downstream analyses or visuals.

## Roadmap & good first issues

1. Implement full arXiv ingestion with paging, retries, and date filtering.
2. Add Crossref enrichment of missing DOIs and venues.
3. Expand the method dictionary with domain expert review and add weakly supervised classifiers.
4. Prototype Negative Binomial models with hierarchical random effects using PyMC.
5. Build a Streamlit dashboard for interactive exploration.

## Citation

If you build on MethodShift, please cite the repository and mention the data sources according to their guidelines.
