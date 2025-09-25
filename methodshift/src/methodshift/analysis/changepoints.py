"""Changepoint detection utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
import ruptures as rpt


@dataclass
class ChangepointResult:
    method: str
    changepoints: List[int]


def detect_changepoints(series: pd.Series, penalty: float = 5.0) -> List[int]:
    """Detect changepoints using the PELT algorithm."""
    algo = rpt.Pelt(model="rbf").fit(series.values)
    cps = algo.predict(pen=penalty)
    return [cp for cp in cps if cp < len(series)]


def changepoints_for_method(df: pd.DataFrame, method: str, penalty: float = 5.0) -> ChangepointResult:
    subset = df[df["method"] == method].sort_values("year")
    series = pd.Series(subset["prevalence"].values, index=subset["year"])
    cps = detect_changepoints(series, penalty=penalty)
    # Map indices back to years
    years = list(series.index)
    changepoint_years = [years[idx - 1] for idx in cps if 0 < idx <= len(years)]
    return ChangepointResult(method=method, changepoints=changepoint_years)


__all__ = ["detect_changepoints", "changepoints_for_method", "ChangepointResult"]
