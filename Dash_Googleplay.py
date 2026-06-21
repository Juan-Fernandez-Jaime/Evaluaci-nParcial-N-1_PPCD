import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# --- Cargar y limpiar datos ---
df = pd.read_csv("./googleplaystore_limpio_2.csv")
df = df.dropna()
df.columns = df.columns.str.strip()

COLOR_MAP = {
    "Free": "#4ECDC4",
    "Paid": "#FF6B6B",
}

BACKGROUND = "#0D1B2A"
CARD_BG    = "#1A2D45"
TEXT       = "#E8F4FD"
ACCENT     = "#4ECDC4"

LAYOUT_BASE = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT, family="IBM Plex Mono, monospace"),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
)

# ---- App ----
app = Dash(__name__)

app.layout = html.Div(
    style={
        "backgroundColor": BACKGROUND,
        "minHeight": "100vh",
        "fontFamily": "IBM Plex Mono, monospace",
        "color": TEXT,
        "padding": "24px",
    },
    children=[

        # Header
        html.Div([
            html.H1(
                "🤖 GOOGLE PLAY STORE DASHBOARD",
                style={"margin": "0", "color": ACCENT, "fontSize": "28px"}
            ),
            html.P(
                "Análisis exploratorio interactivo del mercado de aplicaciones móviles",
                style={"margin": "5px 0 0 0", "opacity": 0.8}
            ),
        ], style={
            "borderBottom": f"2px solid {CARD_BG}",
            "paddingBottom": "15px",
            "marginBottom": "24px"
        }),

        # Filtros
        html.Div([

            html.Div([
                html.Label(
                    "Seleccionar Categorías:",
                    style={
                        "fontWeight": "bold",
                        "marginBottom": "8px",
                        "display": "block"
                    }
                ),

                dcc.Dropdown(
                    id="category-dropdown",
                    options=[
                        {"label": cat, "value": cat}
                        for cat in sorted(df["Category"].unique())
                    ],
                    value=list(df["Category"].unique()[:5]),
                    multi=True,
                    style={
                        "backgroundColor": CARD_BG,
                        "color": "#000"
                    }
                )

            ], style={
                "width": "65%",
                "display": "inline-block"
            }),

            html.Div([
                html.Label(
                    "Tipo de Aplicación:",
                    style={
                        "fontWeight": "bold",
                        "marginBottom": "8px",
                        "display": "block"
                    }
                ),

                dcc.Checklist(
                    id="type-checklist",
                    options=[
                        {"label": t, "value": t}
                        for t in df["Type"].unique()
                        if pd.notna(t)
                    ],
                    value=list(df["Type"].unique()),
                    inline=True,
                    style={
                        "padding": "8px",
                        "backgroundColor": CARD_BG,
                        "borderRadius": "4px"
                    }
                )

            ], style={
                "width": "30%",
                "float": "right"
            }),

        ], style={
            "marginBottom": "24px",
            "overflow": "hidden"
        }),

        # KPIs
        html.Div(
            id="kpi-row",
            style={
                "display": "flex",
                "gap": "15px",
                "marginBottom": "24px",
                "flexWrap": "wrap"
            }
        ),

        # Gráficos fila 1
        html.Div([
            html.Div(
                [dcc.Graph(id="graph-box")],
                style={"width": "49%", "display": "inline-block"}
            ),

            html.Div(
                [dcc.Graph(id="graph-bar")],
                style={
                    "width": "49%",
                    "float": "right",
                    "display": "inline-block"
                }
            ),
        ], style={"marginBottom": "24px"}),

        # Gráficos fila 2
        html.Div([
            html.Div(
                [dcc.Graph(id="graph-hist")],
                style={"width": "49%", "display": "inline-block"}
            ),

            html.Div(
                [dcc.Graph(id="graph-scatter")],
                style={
                    "width": "49%",
                    "float": "right",
                    "display": "inline-block"
                }
            ),
        ]),
    ]
)

# ---- Callbacks ----
@app.callback(
    [
        Output("kpi-row", "children"),
        Output("graph-box", "figure"),
        Output("graph-bar", "figure"),
        Output("graph-hist", "figure"),
        Output("graph-scatter", "figure"),
    ],
    [
        Input("category-dropdown", "value"),
        Input("type-checklist", "value"),
    ]
)
def update_graphs(selected_categories, selected_types):

    if not selected_categories or not selected_types:
        return [], go.Figure(), go.Figure(), go.Figure(), go.Figure()

    d = df[
        df["Category"].isin(selected_categories)
        & df["Type"].isin(selected_types)
    ]

    # KPIs
    total_apps = len(d)
    avg_rating = d["Rating"].mean()
    free_pct = (len(d[d["Type"] == "Free"]) / total_apps) * 100
    avg_reviews = d["Reviews"].mean()

    best_category = (
        d.groupby("Category")["Rating"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    kpi_data = [
        ("📱 Apps", f"{total_apps:,}"),
        ("⭐ Rating", f"{avg_rating:.2f}"),
        ("🆓 Gratis", f"{free_pct:.1f}%"),
        ("💬 Reviews", f"{avg_reviews:,.0f}"),
        ("🏆 Mejor", best_category),
    ]

    kpis = []

    for titulo, valor in kpi_data:
        kpis.append(
            html.Div(
                [
                    html.H4(
                        titulo,
                        style={
                            "margin": "0",
                            "fontSize": "14px",
                            "color": "#8899AA"
                        }
                    ),
                    html.H2(
                        valor,
                        style={
                            "margin": "10px 0",
                            "color": ACCENT
                        }
                    )
                ],
                style={
                    "backgroundColor": CARD_BG,
                    "padding": "15px",
                    "borderRadius": "10px",
                    "flex": "1",
                    "textAlign": "center"
                }
            )
        )

    # BOXPLOT
    fig_box = px.box(
        d,
        x="Category",
        y="Rating",
        color="Type",
        color_discrete_map=COLOR_MAP,
        title="Distribución de Ratings"
    )
    fig_box.update_layout(**LAYOUT_BASE)

    # BARRAS
    counts = d.groupby(
        ["Category", "Type"]
    ).size().reset_index(name="count")

    fig_bar = px.bar(
        counts,
        x="Category",
        y="count",
        color="Type",
        color_discrete_map=COLOR_MAP,
        title="Cantidad de Apps"
    )
    fig_bar.update_layout(**LAYOUT_BASE)

    # HISTOGRAMA
    fig_hist = px.histogram(
        d,
        x="Size",
        color="Type",
        color_discrete_map=COLOR_MAP,
        title="Distribución del Tamaño",
        opacity=0.75
    )
    fig_hist.update_layout(**LAYOUT_BASE)

    # SCATTER
    fig_scatter = px.scatter(
        d,
        x="Reviews",
        y="Relative_Popularity",
        color="Type",
        symbol="Content Rating",
        color_discrete_map=COLOR_MAP,
        title="Popularidad vs Reviews"
    )
    fig_scatter.update_layout(**LAYOUT_BASE)

    return (
        kpis,
        fig_box,
        fig_bar,
        fig_hist,
        fig_scatter
    )

if __name__ == "__main__":
    app.run(debug=True)