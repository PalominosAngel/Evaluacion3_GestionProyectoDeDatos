"""Dashboard de segmentación exploratoria de clientes.

La forma de ejecución se conserva sin cambios:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import theme
from src.data_loader import apply_filters, customer_kpis, load_customers
from src.model import (
    cluster_profile,
    fit_customer_clusters,
    gender_cluster_audit,
)

st.set_page_config(
    page_title="Mall Customers — Segmentación de clientes",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(theme.CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Cargando clientes…")
def get_customers() -> tuple[pd.DataFrame, dict]:
    frame = load_customers()
    return fit_customer_clusters(frame)


customers, model_info = get_customers()

GENDER_COLORS = {"Mujer": "#E76F51", "Hombre": "#457B9D"}

# ---------------------------------------------------------------- sidebar ----

st.sidebar.markdown("### Filtros")

gender_options = ["Mujer", "Hombre"]
selected_genders = st.sidebar.multiselect(
    "Género", options=gender_options, key="filter_genders"
)

education_options = sorted(customers["education"].unique())
selected_education = st.sidebar.multiselect(
    "Educación", options=education_options, key="filter_education"
)

marital_options = sorted(customers["marital_status"].unique())
selected_marital = st.sidebar.multiselect(
    "Estado civil", options=marital_options, key="filter_marital"
)

age_min, age_max = int(customers["age"].min()), int(customers["age"].max())
income_min, income_max = int(customers["annual_income_k"].min()), int(customers["annual_income_k"].max())
spend_min, spend_max = int(customers["spending_score"].min()), int(customers["spending_score"].max())

if "filter_age" not in st.session_state:
    st.session_state["filter_age"] = (age_min, age_max)
if "filter_income" not in st.session_state:
    st.session_state["filter_income"] = (income_min, income_max)
if "filter_spending" not in st.session_state:
    st.session_state["filter_spending"] = (spend_min, spend_max)

selected_age = st.sidebar.slider(
    "Edad", min_value=age_min, max_value=age_max, key="filter_age"
)
selected_income = st.sidebar.slider(
    "Ingreso anual (k$)", min_value=income_min, max_value=income_max, key="filter_income"
)
selected_spending = st.sidebar.slider(
    "Spending Score", min_value=spend_min, max_value=spend_max, key="filter_spending"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Calidad de los datos")

exclude_unknown = st.sidebar.toggle(
    "Excluir categorías Unknown",
    key="filter_exclude_unknown",
    help=(
        "Excluye clientes que tengan 'Unknown' en Education o Marital Status. "
        "El registro original se conserva; este control solo afecta la visualización."
    ),
)

unknown_total = int(customers["has_unknown"].sum())
st.sidebar.caption(
    f"{unknown_total} de {len(customers)} clientes presentan 'Unknown' en educación o estado civil."
)


def reset_filters() -> None:
    st.session_state.update(
        {
            "filter_genders": [],
            "filter_education": [],
            "filter_marital": [],
            "filter_age": (age_min, age_max),
            "filter_income": (income_min, income_max),
            "filter_spending": (spend_min, spend_max),
            "filter_exclude_unknown": False,
        }
    )


st.sidebar.button("Restablecer filtros", width="stretch", on_click=reset_filters)

filtered = apply_filters(
    customers,
    genders=selected_genders,
    education=selected_education,
    marital_status=selected_marital,
    age_range=selected_age,
    income_range=selected_income,
    spending_range=selected_spending,
    exclude_unknown=exclude_unknown,
)

# ----------------------------------------------------------------- header ----

st.markdown(
    """
    <div class="sv-header">
        <h1>Segmentación de clientes — Mall Customers</h1>
        <p>Perfil demográfico, comportamiento de ingreso y gasto, y segmentación K-Means
        para apoyar decisiones del área de marketing</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("La combinación de filtros seleccionada no contiene clientes. Ajuste los criterios en el panel lateral.")
    st.stop()

kpis = customer_kpis(filtered)


def kpi_card(label: str, value: str, hint: str) -> str:
    return (
        f'<div class="sv-kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="hint">{hint}</div></div>'
    )


def es_number(value: float, decimals: int = 0) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "·").replace(".", ",").replace("·", ".")


share = len(filtered) / len(customers) * 100
women_count = int(filtered["gender"].eq("F").sum())

cards = [
    (
        "Clientes seleccionados",
        es_number(kpis["customers"]),
        f"{es_number(share, 1)}% de la muestra total",
    ),
    (
        "Edad promedio",
        es_number(kpis["mean_age"], 1),
        f"Rango seleccionado: {int(filtered['age'].min())}–{int(filtered['age'].max())} años",
    ),
    (
        "Ingreso anual promedio",
        f"{es_number(kpis['mean_income'], 1)} k$",
        "Ingreso anual declarado en el dataset",
    ),
    (
        "Spending Score promedio",
        es_number(kpis["mean_spending"], 1),
        "Escala de 1 a 100",
    ),
    (
        "Participación femenina",
        f"{es_number(kpis['women_pct'], 1)}%",
        f"{women_count} mujeres en la selección",
    ),
    (
        "Educación predominante",
        kpis["top_education"] or "—",
        "Categoría modal de la selección",
    ),
    (
        "Estado civil predominante",
        kpis["top_marital"] or "—",
        "Categoría modal de la selección",
    ),
    (
        "Registros con Unknown",
        f"{es_number(kpis['unknown_pct'], 1)}%",
        f"{kpis['unknown_customers']} clientes afectados",
    ),
]

for row_start in range(0, len(cards), 4):
    for column, (label, value, hint) in zip(st.columns(4), cards[row_start : row_start + 4]):
        column.markdown(kpi_card(label, value, hint), unsafe_allow_html=True)
    st.markdown("")

st.markdown("")

view_profile, view_behavior, view_segments = st.tabs(
    ["Perfil de clientes", "Ingreso y gasto", "Clusters K-Means"]
)

# ------------------------------------------------------ view 1 · profile ----

with view_profile:
    st.markdown("#### ¿Cómo está compuesta la muestra de clientes?")

    left, right = st.columns([1, 1.4])

    with left:
        gender_counts = (
            filtered["gender_label"].value_counts().rename_axis("gender").reset_index(name="customers")
        )
        figure = px.bar(
            gender_counts,
            x="gender",
            y="customers",
            color="gender",
            color_discrete_map=GENDER_COLORS,
            text="customers",
            title="Clientes por género",
        )
        figure.update_traces(textposition="outside", showlegend=False)
        figure.update_layout(xaxis_title="", yaxis_title="Cantidad de clientes", height=380)
        st.plotly_chart(theme.style_figure(figure), width="stretch")

    with right:
        figure = px.histogram(
            filtered,
            x="age",
            nbins=12,
            color="gender_label",
            color_discrete_map=GENDER_COLORS,
            barmode="overlay",
            opacity=0.65,
            title="Distribución de edades",
        )
        figure.update_layout(xaxis_title="Edad", yaxis_title="Cantidad de clientes", height=380)
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    left, right = st.columns(2)

    with left:
        education_counts = (
            filtered["education"].value_counts().rename_axis("education").reset_index(name="customers").sort_values("customers")
        )
        figure = px.bar(
            education_counts,
            x="customers",
            y="education",
            orientation="h",
            color="customers",
            color_continuous_scale=theme.SEQUENTIAL,
            title="Nivel educacional",
        )
        figure.update_layout(
            xaxis_title="Cantidad de clientes", yaxis_title="", height=430, coloraxis_showscale=False
        )
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    with right:
        marital_counts = (
            filtered["marital_status"].value_counts().rename_axis("marital").reset_index(name="customers").sort_values("customers")
        )
        figure = px.bar(
            marital_counts,
            x="customers",
            y="marital",
            orientation="h",
            color="customers",
            color_continuous_scale=theme.SEQUENTIAL,
            title="Estado civil",
        )
        figure.update_layout(
            xaxis_title="Cantidad de clientes", yaxis_title="", height=430, coloraxis_showscale=False
        )
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    st.markdown(
        '<div class="sv-insight">Las categorías <b>Unknown</b> se mantienen visibles para no descartar '
        "registros sin una justificación metodológica. El filtro lateral permite observar el efecto de excluirlas.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------- view 2 · behavior ----

with view_behavior:
    st.markdown("#### ¿Cómo se relacionan el ingreso y el comportamiento de gasto?")

    left, right = st.columns([1.6, 1])

    with left:
        figure = px.scatter(
            filtered,
            x="annual_income_k",
            y="spending_score",
            color="gender_label",
            color_discrete_map=GENDER_COLORS,
            opacity=0.75,
            # RNF01: no CustomerID or per-customer profile fields in the hover.
            hover_data={
                "annual_income_k": ":.0f",
                "spending_score": ":.0f",
            },
            title="Ingreso anual frente a Spending Score",
        )
        figure.update_traces(marker=dict(size=8, line=dict(width=0)))
        figure.update_layout(
            xaxis_title="Ingreso anual (k$)",
            yaxis_title="Spending Score",
            height=470,
        )
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    with right:
        by_gender = filtered.groupby("gender_label", as_index=False).agg(
            income=("annual_income_k", "mean"), spending=("spending_score", "mean")
        )
        figure = px.bar(
            by_gender,
            x="gender_label",
            y=["income", "spending"],
            barmode="group",
            title="Promedios por género",
            labels={"value": "Promedio", "gender_label": "", "variable": "Indicador"},
        )
        figure.update_layout(height=470, legend_title_text="")
        st.plotly_chart(theme.style_figure(figure), width="stretch")

    st.markdown(
        '<div class="sv-insight">El Spending Score es un índice de comportamiento de gasto entre 1 y 100. '
        "El diagrama permite identificar visualmente grupos con combinaciones distintas de ingreso y gasto, "
        "sin asumir todavía que esos grupos constituyen clusters definitivos.</div>",
        unsafe_allow_html=True,
    )

    # RNF01: aggregated bands replace the former per-customer ranking table.
    st.markdown("##### Perfil agregado por tramo de Spending Score")
    spending_bands = pd.cut(
        filtered["spending_score"],
        bins=[0, 20, 40, 60, 80, 100],
        labels=["1–20", "21–40", "41–60", "61–80", "81–100"],
    )
    band_summary = (
        filtered.assign(band=spending_bands)
        .groupby("band", observed=True)
        .agg(
            Clientes=("spending_score", "size"),
            Edad_promedio=("age", "mean"),
            Ingreso_promedio=("annual_income_k", "mean"),
        )
        .reset_index()
        .rename(columns={"band": "Tramo de Spending Score"})
    )
    st.dataframe(
        band_summary,
        width="stretch",
        hide_index=True,
        column_config={
            "Edad_promedio": st.column_config.NumberColumn("Edad promedio", format="%.1f"),
            "Ingreso_promedio": st.column_config.NumberColumn("Ingreso promedio (k$)", format="%.1f"),
        },
    )

# ---------------------------------------------------- view 3 · clusters ----

with view_segments:
    st.markdown("#### Segmentación K-Means de clientes")
    st.caption(
        f"Modelo final: k = {model_info['k']} · coeficiente de silueta = "
        f"{model_info['silhouette']:.3f} · variables estandarizadas: edad, ingreso anual y Spending Score."
    )

    left, right = st.columns([1.45, 1])

    with left:
        figure = px.scatter(
            filtered,
            x="annual_income_k",
            y="spending_score",
            color="cluster",
            opacity=0.82,
            # RNF01: no CustomerID or per-customer profile fields in the hover.
            hover_data={
                "annual_income_k": ":.0f",
                "spending_score": ":.0f",
            },
            title="Clusters sobre ingreso y Spending Score",
        )
        figure.update_traces(marker=dict(size=9, line=dict(width=0)))
        figure.update_layout(
            xaxis_title="Ingreso anual (k$)",
            yaxis_title="Spending Score",
            height=500,
            legend_title_text="Cluster",
        )
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    with right:
        cluster_counts = (
            filtered.groupby(["cluster_id", "cluster"], observed=True)
            .size()
            .reset_index(name="Clientes")
            .sort_values("cluster_id")
        )
        figure = px.bar(
            cluster_counts,
            x="Clientes",
            y="cluster",
            orientation="h",
            color="Clientes",
            color_continuous_scale=theme.SEQUENTIAL,
            text="Clientes",
            title="Tamaño de los clusters",
        )
        figure.update_layout(
            xaxis_title="Cantidad de clientes",
            yaxis_title="",
            height=500,
            coloraxis_showscale=False,
        )
        st.plotly_chart(theme.style_figure(figure, show_xgrid=True), width="stretch")

    st.markdown(
        '<div class="sv-insight">El modelo utiliza <b>K-Means</b> sobre edad, ingreso anual y '
        'Spending Score previamente estandarizados. El valor de <b>k</b> se seleccionó evaluando '
        'candidatos entre 2 y 10 mediante inercia (método del codo) y coeficiente de silueta; '
        'para este dataset, k = 6 obtiene la mayor silueta entre los candidatos evaluados.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("##### Perfil resumido por cluster")
    summary = cluster_profile(filtered).drop(columns=["cluster_id"])
    st.dataframe(
        summary,
        width="stretch",
        hide_index=True,
        column_config={
            "Edad_promedio": st.column_config.NumberColumn("Edad promedio", format="%.1f"),
            "Ingreso_promedio": st.column_config.NumberColumn("Ingreso promedio (k$)", format="%.1f"),
            "Spending_promedio": st.column_config.NumberColumn("Spending Score promedio", format="%.1f"),
        },
    )

    st.markdown("##### Revisión de distribución por género")
    gender_audit = gender_cluster_audit(filtered)
    figure = px.bar(
        gender_audit,
        x="cluster",
        y="Porcentaje",
        color="gender_label",
        color_discrete_map=GENDER_COLORS,
        barmode="stack",
        text=gender_audit["Porcentaje"].map(lambda value: f"{value:.1f}%"),
        title="Composición de género dentro de cada cluster",
    )
    figure.update_layout(
        xaxis_title="",
        yaxis_title="Porcentaje dentro del cluster",
        height=430,
        legend_title_text="Género",
        yaxis_range=[0, 100],
    )
    st.plotly_chart(theme.style_figure(figure), width="stretch")

    st.markdown(
        '<div class="sv-warning"><b>Limitaciones de la revisión de sesgos:</b> el género no se utiliza '
        'como variable de entrenamiento del K-Means; la comparación solo permite observar cómo se '
        'distribuyen mujeres y hombres dentro de los clusters. Las diferencias observadas no demuestran '
        'por sí solas discriminación. Además, la muestra contiene solo 200 clientes y existen categorías '
        '<i>Unknown</i> en educación y estado civil, por lo que los resultados no deben generalizarse sin '
        'validación adicional.</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "Gestión de Proyectos de Datos (SCY1102) · Proyecto de segmentación de clientes · "
    "Fuente: Mall Customers.xlsx · 200 registros"
)
