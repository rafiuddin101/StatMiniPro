"""Summary metrics for method diffusion."""
from __future__ import annotations

import numpy as np
import pandas as pd


def compound_annual_growth_rate(counts: pd.Series) -> float:
    if counts.empty or (counts.iloc[0] <= 0) or (counts.iloc[-1] <= 0):
        return 0.0
    periods = len(counts) - 1
    if periods <= 0:
        return 0.0
    return (counts.iloc[-1] / counts.iloc[0]) ** (1 / periods) - 1


def cross_correlation(series_a: pd.Series, series_b: pd.Series, lag: int = 0) -> float:
    if lag > 0:
        series_a = series_a.iloc[:-lag]
        series_b = series_b.iloc[lag:]
    elif lag < 0:
        series_a = series_a.iloc[-lag:]
        series_b = series_b.iloc[:lag]
    if len(series_a) != len(series_b) or len(series_a) == 0:
        return float("nan")
    return float(np.corrcoef(series_a, series_b)[0, 1])


__all__ = ["compound_annual_growth_rate", "cross_correlation"]
