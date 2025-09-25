"""Modeling utilities for method adoption trends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class TrendResult:
    method: str
    params: pd.Series
    model: sm.GLM
    year_mean: float


def build_design_matrix(df: pd.DataFrame, method: str) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare a design matrix for GLM modeling of method prevalence."""
    subset = df[df["method"] == method].copy()
    year_mean = subset["year"].mean()
    subset["year_centered"] = subset["year"] - year_mean
    subset["intercept"] = 1.0
    X = subset[["intercept", "year_centered"]]
    y = subset["count"]
    return X, y, year_mean


def fit_poisson_glm(df: pd.DataFrame, method: str) -> TrendResult:
    X, y, year_mean = build_design_matrix(df, method)
    model = sm.GLM(y, X, family=sm.families.Poisson())
    results = model.fit()
    return TrendResult(method=method, params=results.params, model=model, year_mean=year_mean)


def predict_counts(result: TrendResult, years: Iterable[int]) -> pd.DataFrame:
    X = pd.DataFrame({"intercept": 1.0, "year_centered": np.array(list(years)) - result.year_mean})
    mu = result.model.predict(X)
    return pd.DataFrame({"year": list(years), "expected_count": mu})


__all__ = ["TrendResult", "fit_poisson_glm", "predict_counts", "build_design_matrix"]
