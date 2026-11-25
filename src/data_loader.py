"""Carga y preparación del dataset Mall Customers para el dashboard.

El proyecto conserva la misma forma de ejecución del dashboard original. La
adaptación se limita a leer el nuevo dataset y exponer variables coherentes con
el caso de segmentación de clientes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DATA_FILE = "mall_customers.csv"

GENDER_LABELS = {"F": "Mujer", "M": "Hombre"}


def load_customers() -> pd.DataFrame:
    """Cargar y normalizar el dataset Mall Customers."""
    frame = pd.read_csv(RAW_DIR / DATA_FILE)
    frame = frame.rename(
        columns={
            "CustomerID": "customer_id",
            "Gender": "gender",
            "Age": "age",
            "Education": "education",
            "Marital Status": "marital_status",
            "Annual Income (k$)": "annual_income_k",
            "Spending Score (1-100)": "spending_score",
        }
    )

    frame["gender_label"] = frame["gender"].map(GENDER_LABELS).fillna(frame["gender"])
    frame["education"] = frame["education"].fillna("Unknown")
    frame["marital_status"] = frame["marital_status"].fillna("Unknown")
    frame["has_unknown"] = (
        frame["education"].eq("Unknown") | frame["marital_status"].eq("Unknown")
    )

    return frame


def apply_filters(
    frame: pd.DataFrame,
    genders: list[str] | None = None,
    education: list[str] | None = None,
    marital_status: list[str] | None = None,
    age_range: tuple[int, int] | None = None,
    income_range: tuple[int, int] | None = None,
    spending_range: tuple[int, int] | None = None,
    exclude_unknown: bool = False,
) -> pd.DataFrame:
    """Aplicar los filtros seleccionados en el panel lateral."""
    filtered = frame

    if genders:
        filtered = filtered[filtered["gender_label"].isin(genders)]
    if education:
        filtered = filtered[filtered["education"].isin(education)]
    if marital_status:
        filtered = filtered[filtered["marital_status"].isin(marital_status)]
    if age_range:
        filtered = filtered[filtered["age"].between(*age_range)]
    if income_range:
        filtered = filtered[filtered["annual_income_k"].between(*income_range)]
    if spending_range:
        filtered = filtered[filtered["spending_score"].between(*spending_range)]
    if exclude_unknown:
        filtered = filtered[~filtered["has_unknown"]]

    return filtered


def customer_kpis(frame: pd.DataFrame) -> dict[str, float | int | str | None]:
    """Indicadores principales de la selección actual."""
    if frame.empty:
        return {
            "customers": 0,
            "mean_age": None,
            "mean_income": None,
            "mean_spending": None,
            "women_pct": None,
            "top_education": None,
            "top_marital": None,
            "unknown_pct": None,
            "unknown_customers": 0,
        }

    total = len(frame)
    women = int(frame["gender"].eq("F").sum())
    unknown_customers = int(frame["has_unknown"].sum())

    return {
        "customers": total,
        "mean_age": float(frame["age"].mean()),
        "mean_income": float(frame["annual_income_k"].mean()),
        "mean_spending": float(frame["spending_score"].mean()),
        "women_pct": women / total * 100,
        "top_education": str(frame["education"].mode().iloc[0]),
        "top_marital": str(frame["marital_status"].mode().iloc[0]),
        "unknown_pct": unknown_customers / total * 100,
        "unknown_customers": unknown_customers,
    }
