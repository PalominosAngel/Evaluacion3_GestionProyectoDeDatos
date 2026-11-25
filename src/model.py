"""Modelo compartido de segmentación K-Means para Mall Customers.

El notebook y el dashboard importan este módulo para asegurar que la selección
de variables, estandarización, parámetros y asignación de clusters sean los
mismos en ambos entregables.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

MODEL_FEATURES = ["age", "annual_income_k", "spending_score"]
K_CANDIDATES = tuple(range(2, 11))
RANDOM_STATE = 42
N_INIT = 20


def _validate_features(frame: pd.DataFrame) -> None:
    missing = [column for column in MODEL_FEATURES if column not in frame.columns]
    if missing:
        raise ValueError(f"Faltan variables requeridas para K-Means: {missing}")
    if frame[MODEL_FEATURES].isna().any().any():
        raise ValueError("Las variables de K-Means contienen valores nulos.")


def _scaled_features(frame: pd.DataFrame) -> tuple[StandardScaler, object]:
    _validate_features(frame)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(frame[MODEL_FEATURES])
    return scaler, scaled


def evaluate_k_candidates(
    frame: pd.DataFrame,
    candidates: Iterable[int] = K_CANDIDATES,
) -> pd.DataFrame:
    """Evaluar candidatos de k mediante inercia y coeficiente de silueta."""
    _, scaled = _scaled_features(frame)
    rows: list[dict[str, float | int]] = []

    for k in candidates:
        if k < 2 or k >= len(frame):
            continue
        model = KMeans(
            n_clusters=int(k),
            random_state=RANDOM_STATE,
            n_init=N_INIT,
        )
        labels = model.fit_predict(scaled)
        rows.append(
            {
                "k": int(k),
                "inertia": float(model.inertia_),
                "silhouette": float(silhouette_score(scaled, labels)),
            }
        )

    if not rows:
        raise ValueError("No existen valores de k válidos para evaluar.")

    return pd.DataFrame(rows)


def choose_k(frame: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    """Elegir k por el mayor coeficiente de silueta entre los candidatos.

    La curva de inercia se entrega en la misma tabla para revisar también el
    método del codo. En Mall Customers, ambos criterios se revisan en el
    notebook antes de fijar el modelo final.
    """
    metrics = evaluate_k_candidates(frame)
    best_row = metrics.sort_values(
        ["silhouette", "k"], ascending=[False, True]
    ).iloc[0]
    return int(best_row["k"]), metrics


def fit_customer_clusters(
    frame: pd.DataFrame,
    k: int | None = None,
) -> tuple[pd.DataFrame, dict[str, float | int | list[str]]]:
    """Estandarizar variables y ajustar K-Means sobre el dataset completo.

    Si ``k`` no se entrega, se selecciona automáticamente el candidato con
    mayor coeficiente de silueta. Los números de cluster se reordenan por los
    centroides de ingreso, gasto y edad para mantener etiquetas estables y
    legibles entre notebook y dashboard.
    """
    scaler, scaled = _scaled_features(frame)

    if k is None:
        k, _ = choose_k(frame)

    if k < 2 or k >= len(frame):
        raise ValueError("k debe ser al menos 2 y menor que el número de clientes.")

    model = KMeans(
        n_clusters=int(k),
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    raw_labels = model.fit_predict(scaled)

    centers_original = scaler.inverse_transform(model.cluster_centers_)
    # Orden estable: ingreso, gasto y edad. El número interno de K-Means es
    # arbitrario; este remapeo solo hace reproducible la presentación.
    center_order = sorted(
        range(int(k)),
        key=lambda idx: (
            centers_original[idx][1],
            centers_original[idx][2],
            centers_original[idx][0],
        ),
    )
    label_map = {raw_label: position + 1 for position, raw_label in enumerate(center_order)}

    result = frame.copy()
    result["cluster_id"] = [label_map[int(label)] for label in raw_labels]
    result["cluster"] = result["cluster_id"].map(lambda value: f"Cluster {value}")

    info: dict[str, float | int | list[str]] = {
        "k": int(k),
        "silhouette": float(silhouette_score(scaled, raw_labels)),
        "inertia": float(model.inertia_),
        "random_state": RANDOM_STATE,
        "n_init": N_INIT,
        "features": list(MODEL_FEATURES),
    }
    return result, info


def cluster_profile(frame: pd.DataFrame) -> pd.DataFrame:
    """Describir tamaño, edad, ingreso y Spending Score de cada cluster."""
    return (
        frame.groupby(["cluster_id", "cluster"], as_index=False, observed=True)
        .agg(
            Clientes=("customer_id", "count"),
            Edad_promedio=("age", "mean"),
            Ingreso_promedio=("annual_income_k", "mean"),
            Spending_promedio=("spending_score", "mean"),
        )
        .sort_values("cluster_id")
        .reset_index(drop=True)
    )


def gender_cluster_audit(frame: pd.DataFrame) -> pd.DataFrame:
    """Distribución por género dentro de cada cluster para revisión de sesgos."""
    counts = (
        frame.groupby(["cluster_id", "cluster", "gender_label"], observed=True)
        .size()
        .reset_index(name="Clientes")
    )
    totals = counts.groupby("cluster_id")["Clientes"].transform("sum")
    counts["Porcentaje"] = counts["Clientes"] / totals * 100
    return counts.sort_values(["cluster_id", "gender_label"]).reset_index(drop=True)
