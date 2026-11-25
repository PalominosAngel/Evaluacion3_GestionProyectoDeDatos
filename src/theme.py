"""
Visual system for the dashboard.

The palette extends the one already used in the report's visual narrative, so
the dashboard and the document read as a single product.

Movies and TV shows are encoded with blue and orange rather than the more
obvious blue and green pair: blue/orange stays distinguishable under the most
common forms of colour vision deficiency, while blue/green does not. The same
two colours mean the same two things in every chart of the dashboard.
"""

# Content type encoding — fixed across the whole dashboard.
COLOR_MOVIES = "#4A7DBF"
COLOR_TV = "#E08A3C"

# Structural colours.
COLOR_INK = "#16243D"
COLOR_MUTED = "#6B7A90"
COLOR_GRID = "#E4E9F0"
COLOR_SURFACE = "#FFFFFF"
COLOR_ACCENT = "#3E9E86"

TYPE_COLORS = {
    "Películas": COLOR_MOVIES,
    "Series": COLOR_TV,
}

# Sequential ramp for single-series charts (genres, countries, years).
SEQUENTIAL = [
    "#D6E2F2",
    "#AEC6E6",
    "#86A9D9",
    "#5E8DCD",
    "#4A7DBF",
    "#3A6399",
]

BASE_LAYOUT = dict(
    font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", size=13, color=COLOR_INK),
    title=dict(font=dict(size=16, color=COLOR_INK), x=0, xanchor="left"),
    paper_bgcolor=COLOR_SURFACE,
    plot_bgcolor=COLOR_SURFACE,
    margin=dict(l=10, r=10, t=50, b=10),
    hoverlabel=dict(font_size=12, bgcolor=COLOR_INK, font_color="white"),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title_text=""),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor=COLOR_GRID,
    zeroline=False,
    linecolor=COLOR_GRID,
    tickfont=dict(color=COLOR_MUTED),
)


def style_figure(figure, show_xgrid: bool = False):
    """Apply the shared layout to a Plotly figure."""
    figure.update_layout(**BASE_LAYOUT)
    figure.update_xaxes(**{**AXIS_STYLE, "showgrid": show_xgrid})
    figure.update_yaxes(**AXIS_STYLE)
    return figure


CUSTOM_CSS = """
<style>
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px; }

    .sv-header {
        background: linear-gradient(135deg, #16243D 0%, #24395C 100%);
        color: #FFFFFF;
        padding: 1.4rem 1.8rem;
        border-radius: 10px;
        margin-bottom: 1.6rem;
    }
    .sv-header h1 { font-size: 1.6rem; margin: 0 0 .3rem 0; font-weight: 700; }
    .sv-header p { margin: 0; opacity: .82; font-size: .92rem; }

    .sv-kpi {
        background: #FFFFFF;
        border: 1px solid #E4E9F0;
        border-left: 4px solid #4A7DBF;
        border-radius: 8px;
        padding: .9rem 1.1rem;
        height: 100%;
        min-height: 7.9rem;
    }
    .sv-kpi .label {
        font-size: .74rem;
        text-transform: uppercase;
        letter-spacing: .04em;
        color: #6B7A90;
        margin-bottom: .3rem;
    }
    .sv-kpi .value { font-size: 1.7rem; font-weight: 700; color: #16243D; line-height: 1.1; }
    .sv-kpi .hint { font-size: .74rem; color: #6B7A90; margin-top: .25rem; }

    .sv-insight {
        background: #F4F7FB;
        border-left: 4px solid #3E9E86;
        border-radius: 6px;
        padding: .85rem 1.1rem;
        font-size: .88rem;
        color: #2B3A52;
        margin-top: .6rem;
    }
    .sv-warning {
        background: #FDF6EC;
        border-left: 4px solid #E08A3C;
        border-radius: 6px;
        padding: .85rem 1.1rem;
        font-size: .88rem;
        color: #4A3520;
        margin-top: .6rem;
    }
    section[data-testid="stSidebar"] { background: #F7F9FC; }
</style>
"""
