import warnings
from datetime import datetime

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# =========================================================
# Config
# =========================================================
DATA_PATH = "pnadc.xlsx"  # ou "pnad.csv" / "pnad.csv.gz"
APP_TITLE = "Dashboard PNAD Contínua"

# Paleta
colors = {
    "primary": "#053042",
    "secondary": "#AF200D",
    "accent": "#8B590D",
    "success": "#2E7D32",
    "background": "#F5F5F5",
    "card": "#FFFFFF",
}

# Estilos aba
tab_style = {
    "padding": "10px",
    "fontWeight": "bold",
    "border": "1px solid #ddd",
    "background": "#fafafa",
}
tab_selected_style = {
    "padding": "10px",
    "fontWeight": "bold",
    "border": "1px solid #053042",
    "background": "#fff",
    "color": "#053042",
}

# =========================================================
# Helper: leitura robusta
# =========================================================
def load_data(path: str) -> pd.DataFrame:
    path_l = path.lower()
    if path_l.endswith(".parquet"):
        return pd.read_parquet(path)
    if path_l.endswith(".csv") or path_l.endswith(".csv.gz"):
        return pd.read_csv(path)
    if path_l.endswith(".xlsx") or path_l.endswith(".xls"):
        # engine openpyxl para .xlsx
        return pd.read_excel(path)  # se precisar: pd.read_excel(path, engine="openpyxl")
    # fallback
    try:
        return pd.read_parquet(path)
    except Exception:
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.read_excel(path)

df = load_data(DATA_PATH)

# =========================================================
# Garantias de tipos mínimos
# =========================================================
num_cols = [
    "Ano","Trimestre","UF","Capital","RM_RIDE","UPA","Estrato","V1008","V1014","V1016",
    "V1022","V1023","V1027","V1028","V1029","V1033","posest","posest_sxi",
    "V2001","V2003","V2005","V2007","V2008","V20081","V20082","V2009","V2010",
    "V4001","V4002","V4003","V4004","V4005","V4006","V4006A","V4007","V4008",
    "V40081","V40082","V40083",
]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# =========================================================
# Placeholders de ML (implemente depois)
# =========================================================
def predict_labor_market_indicators(df_in: pd.DataFrame):
    # TODO: implementar modelo de previsão de indicadores do mercado de trabalho
    # Retorne um DataFrame com colunas como ["UF","Trimestre","indicador_previsto",...]
    return None, None  # (prediction_df, feature_importance_dict)

prediction_df, feature_importance = predict_labor_market_indicators(df)

# =========================================================
# Métricas básicas (exemplos PNAD)
# =========================================================
def compute_kpis(dfx: pd.DataFrame):
    # Exemplos de KPIs simples:
    # - total de registros (pessoas)
    total = len(dfx)

    # - média de idade aproximada (se V2009=ano nascimento, V2010=mês? depende do layout completo)
    # Caso não exista idade, omitir. Aqui, exemplo com V2009 como idade declarada se existir.
    # Ajuste conforme seu dicionário completo.
    idade_media = dfx["V2009"].mean() if "V2009" in dfx.columns else None

    # - taxa de ocupação aproximada (ex.: V4001 = força de trabalho? V4002 ocupado? Depende do dicionário)
    # Aqui coloco placeholders: se V4002==1 (ocupado), taxa = ocupados / total válidos
    taxa_ocup = None
    if "V4002" in dfx.columns:
        valid = dfx["V4002"].notna()
        if valid.any():
            taxa_ocup = (dfx.loc[valid, "V4002"].eq(1).sum() / valid.sum()) * 100

    # - média de rendimento (ex.: V403312/V403412 etc., não listadas em seu subset; usaremos V1028 como peso apenas em gráfico)
    return dict(
        total=total,
        idade_media=idade_media,
        taxa_ocup=taxa_ocup,
    )

# =========================================================
# App
# =========================================================
app = dash.Dash(__name__, suppress_callback_exceptions=True, title=APP_TITLE)

# Filtros de topo
uf_opts = sorted(d for d in df["UF"].dropna().unique()) if "UF" in df.columns else []
ano_opts = sorted(d for d in df["Ano"].dropna().unique()) if "Ano" in df.columns else []
tri_opts = sorted(d for d in df["Trimestre"].dropna().unique()) if "Trimestre" in df.columns else []

def kpi_card(id_, label, color):
    return html.Div(
        [
            html.Div(
                [
                    html.H3(id=id_, style={"color": color, "margin": 0}),
                    html.P(label, style={"margin": 0}),
                ],
                className="kpi-card",
                style={
                    "background": colors["card"],
                    "padding": 20,
                    "borderRadius": 8,
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                },
            )
        ],
        style={"width": "19%", "display": "inline-block", "margin": "0.5%"},
    )

app.layout = html.Div(
    [
        html.H1(
            APP_TITLE,
            style={"textAlign": "center", "color": colors["primary"], "marginBottom": 10},
        ),
        # Painel de filtros globais
        html.Div(
            [
                html.Div(
                    [
                        html.Label("UF"),
                        dcc.Dropdown(
                            id="f-uf",
                            options=[{"label": str(u), "value": u} for u in uf_opts],
                            value=None,
                            multi=True,
                            placeholder="Selecione UF(s)",
                            style={"width": "200px"},
                        ),
                    ],
                    style={"marginRight": 20},
                ),
                html.Div(
                    [
                        html.Label("Ano"),
                        dcc.Dropdown(
                            id="f-ano",
                            options=[{"label": str(a), "value": a} for a in ano_opts],
                            value=None,
                            multi=True,
                            placeholder="Selecione Ano(s)",
                            style={"width": "200px"},
                        ),
                    ],
                    style={"marginRight": 20},
                ),
                html.Div(
                    [
                        html.Label("Trimestre"),
                        dcc.Dropdown(
                            id="f-tri",
                            options=[{"label": str(t), "value": t} for t in tri_opts],
                            value=None,
                            multi=True,
                            placeholder="Selecione Trimestre(s)",
                            style={"width": "200px"},
                        ),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "flex-end",
                "gap": 20,
                "background": colors["card"],
                "padding": 15,
                "borderRadius": 8,
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "margin": "10px 0 20px 0",
            },
        ),
        # KPIs
        html.Div(
            [
                kpi_card("kpi-total", "Total de Registros", colors["primary"]),
                kpi_card("kpi-idade-media", "Idade Média (aprox.)", colors["accent"]),
                kpi_card("kpi-taxa-ocup", "Taxa de Ocupação (aprox.)", colors["secondary"]),
                kpi_card("kpi-uf-dist", "UF mais frequente", colors["success"]),
                kpi_card("kpi-tri-dist", "Trimestre mais frequente", colors["primary"]),
            ],
            style={"marginBottom": 20},
        ),
        # Abas
        dcc.Tabs(
            id="tabs",
            value="visao",
            children=[
                dcc.Tab(label="Visão Geral", value="visao", style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label="Distribuições", value="dist", style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label="Previsões (ML)", value="ml", style=tab_style, selected_style=tab_selected_style),
            ],
        ),
        html.Div(id="tab-content"),
    ],
    style={"padding": 20, "backgroundColor": colors["background"], "minHeight": "100vh"},
)

# =========================================================
# Filtro base
# =========================================================
def apply_filters(dfx: pd.DataFrame, ufs, anos, tris):
    out = dfx
    if ufs:
        out = out[out["UF"].isin(ufs)]
    if anos:
        out = out[out["Ano"].isin(anos)]
    if tris:
        out = out[out["Trimestre"].isin(tris)]
    return out

# =========================================================
# Callbacks: KPIs
# =========================================================
@app.callback(
    [
        Output("kpi-total", "children"),
        Output("kpi-idade-media", "children"),
        Output("kpi-taxa-ocup", "children"),
        Output("kpi-uf-dist", "children"),
        Output("kpi-tri-dist", "children"),
    ],
    [Input("f-uf", "value"), Input("f-ano", "value"), Input("f-tri", "value")],
)
def update_kpis(ufs, anos, tris):
    dff = apply_filters(df, ufs, anos, tris)
    k = compute_kpis(dff)

    uf_mode = dff["UF"].mode().iloc[0] if ("UF" in dff and len(dff) > 0 and not dff["UF"].mode().empty) else "-"
    tri_mode = dff["Trimestre"].mode().iloc[0] if ("Trimestre" in dff and len(dff) > 0 and not dff["Trimestre"].mode().empty) else "-"

    return (
        f"{k['total']:,}".replace(",", "."),
        "-" if k["idade_media"] is None or pd.isna(k["idade_media"]) else f"{k['idade_media']:.1f}",
        "-" if k["taxa_ocup"] is None or pd.isna(k["taxa_ocup"]) else f"{k['taxa_ocup']:.1f}%",
        str(uf_mode),
        str(tri_mode),
    )

# =========================================================
# Conteúdo das abas
# =========================================================
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("f-uf", "value"), Input("f-ano", "value"), Input("f-tri", "value")],
)
def render_tab(active_tab, ufs, anos, tris):
    dff = apply_filters(df, ufs, anos, tris)

    if active_tab == "ml":
        # Placeholders gráficos ML
        # prediction_df e feature_importance virão da função a implementar
        if prediction_df is None:
            return html.Div(
                [
                    html.H3("Previsões (ML)"),
                    html.P("Modelo ainda não disponível. Em breve: indicadores previstos por UF/Ano/Trimestre."),
                ],
                style={"background": colors["card"], "padding": 20, "borderRadius": 8},
            )

        # Exemplo de uso quando existir:
        # fig_import = px.bar(x=list(feature_importance.values()), y=list(feature_importance.keys()), orientation="h")
        # return html.Div([dcc.Graph(figure=fig_import)], style={"background": colors["card"], "padding": 20, "borderRadius": 8})

        return html.Div()

    if active_tab == "dist":
        # Distribuições básicas
        figs = []

        # Distribuição por UF
        if "UF" in dff.columns and len(dff) > 0:
            cnt = dff["UF"].value_counts().reset_index()
            cnt.columns = ["UF", "count"]
            figs.append(
                dcc.Graph(
                    figure=px.bar(
                        cnt, x="UF", y="count", title="Distribuição por UF", color="UF"
                    ).update_layout(showlegend=False)
                )
            )

        # Distribuição por Trimestre
        if "Trimestre" in dff.columns and len(dff) > 0:
            cnt = dff["Trimestre"].value_counts().reset_index()
            cnt.columns = ["Trimestre", "count"]
            figs.append(
                dcc.Graph(
                    figure=px.bar(
                        cnt, x="Trimestre", y="count", title="Distribuição por Trimestre", color="Trimestre"
                    ).update_layout(showlegend=False)
                )
            )

        # Histograma (ex.: V1028 peso amostral)
        if "V1028" in dff.columns and dff["V1028"].notna().any():
            figs.append(
                dcc.Graph(
                    figure=px.histogram(
                        dff, x="V1028", nbins=30, title="Distribuição do Peso Amostral (V1028)"
                    )
                )
            )

        # Barras para variáveis categóricas curtas (ex.: V1022/V1023 situação urbana/rural/domicílio)
        for col in ["V1022", "V1023", "V4002"]:
            if col in dff.columns and dff[col].notna().any():
                vc = dff[col].value_counts().reset_index()
                vc.columns = [col, "count"]
                figs.append(
                    dcc.Graph(
                        figure=px.bar(vc, x=col, y="count", title=f"Distribuição de {col}").update_layout(showlegend=False)
                    )
                )

        if not figs:
            return html.Div("Sem dados para exibir.", style={"padding": 20})

        return html.Div(figs, style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": 20})

    # Visão Geral
    cards = []
    # Exemplo: série temporal por Ano/Trimestre (contagem de registros)
    if "Ano" in dff.columns and "Trimestre" in dff.columns and len(dff) > 0:
        tmp = (
            dff.groupby(["Ano", "Trimestre"])
            .size()
            .reset_index(name="count")
            .sort_values(["Ano", "Trimestre"])
        )
        tmp["Periodo"] = tmp["Ano"].astype(str) + "T" + tmp["Trimestre"].astype(int).astype(str)
        fig_ts = px.line(tmp, x="Periodo", y="count", title="Registros por Período (Ano/Trimestre)")
        cards.append(dcc.Graph(figure=fig_ts))

    # Exemplo: Mapa coroplético por UF (contagem) — requer UF como código 1..27
    if "UF" in dff.columns and len(dff) > 0:
        # dff["UF"] é numérico (1..27). Para mapa, podemos usar um bar por UF (simples).
        by_uf = dff["UF"].value_counts().reset_index()
        by_uf.columns = ["UF", "count"]
        fig_bar = px.bar(by_uf.sort_values("UF"), x="UF", y="count", title="Registros por UF")
        cards.append(dcc.Graph(figure=fig_bar))

    # Exemplo: relação V1028 por UF (box)
    if "UF" in dff.columns and "V1028" in dff.columns and dff["V1028"].notna().any():
        fig_box = px.box(dff, x="UF", y="V1028", title="Peso Amostral (V1028) por UF")
        cards.append(dcc.Graph(figure=fig_box))

    return html.Div(cards, style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": 20})

# =========================================================
# Run
# =========================================================
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)