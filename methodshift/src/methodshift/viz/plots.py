"""Visualization utilities."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_method_trend(df: pd.DataFrame, method: str) -> plt.Axes:
    subset = df[df["method"] == method].sort_values("year")
    fig, ax = plt.subplots()
    ax.plot(subset["year"], subset["prevalence"], marker="o")
    ax.set_title(f"{method.title()} prevalence")
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of abstracts")
    return ax


__all__ = ["plot_method_trend"]
