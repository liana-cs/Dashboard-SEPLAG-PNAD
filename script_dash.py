import warnings

import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

warnings.filterwarnings("ignore")

# --------------------------------------------
# Carregar tabela consolidada
# --------------------------------------------
DATA_PATH = "tabela_final_empregadores_contapropria_ponderada_2021.parquet"

df = pd.read_parquet(DATA_PATH)

# Garantir tipos
if "Trimestre" in df.columns:
    # pode ser "1T2021", "2T2021", etc.
    df["Trimestre"] = df["Trimestre"].astype(str)

# Lista de trimestres ordenada
tri_opts = sorted(df["Trimestre"].unique())

# Paleta e estilos
colors = {
    "primary": "#053042",
    "secondary": "#AF200D",
    "accent": "#8B590D",
    "success": "#2E7D32",
    "background": "#F5F5F5",
    "card": "#FFFFFF",
}

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

# --------------------------------------------
# App
# --------------------------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True, title="PNAD – Empregadores e Conta Própria")

app.layout = html.Div(
    [
        html.H1(
            "PNAD Contínua – Empregadores e Conta Própria (PE, 2021)",
            style={"textAlign": "center", "color": colors["primary"], "marginBottom": 10},
        ),
        dcc.Tabs(
            id="tabs",
            value="apresentacao",
            children=[
                dcc.Tab(
                    label="Apresentação",
                    value="apresentacao",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Total Ocupados",
                    value="total",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Empregadores",
                    value="empregador",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Conta Própria",
                    value="conta_propria",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
            ],
        ),
        html.Div(id="tab-content"),
    ],
    style={"padding": 20, "backgroundColor": colors["background"], "minHeight": "100vh"},
)

# --------------------------------------------
# Conteúdo das abas
# --------------------------------------------
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
)
def render_tab(tab): 
    if tab == "apresentacao":
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Sobre as Informações", style={"color": colors["primary"]}),
                        html.P(
                            [
                                "Este painel utiliza dados da ",
                                html.B("PNAD Contínua (IBGE)"),
                                " para o estado de Pernambuco (UF=26), ano de 2021, ",
                                "com foco em ocupação, renda do trabalho principal, trabalho secundário e outros rendimentos ",
                                "para três grupos: total de ocupados, empregadores e conta própria.",
                            ]
                        ),
                        html.H3("Definições das Variáveis (ponderadas)", style={"marginTop": 20}),
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.B("n_ocup_pond"),
                                        ": número de ocupados ponderado (soma dos pesos amostrais V1028).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("renda_total_pond"),
                                        ": soma ponderada da renda total do trabalho (principal + secundário + outros).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("Renda Média_Total"),
                                        ": renda média do trabalho para o total de ocupados (renda_total_pond / n_ocup_pond).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("n_empregador_pond"),
                                        ": número ponderado de empregadores (V4012=5 e V40161=1).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("renda_empregador_pond"),
                                        ": renda total ponderada dos empregadores.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("Renda Média_empregador"),
                                        ": renda média do trabalho para empregadores.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("n_conta_propria_pond"),
                                        ": número ponderado de conta própria (V4012=6).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("renda_conta_propria_pond"),
                                        ": renda total ponderada dos conta própria.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.B("Renda Média_conta_propria"),
                                        ": renda média do trabalho para conta própria.",
                                    ]
                                ),
                            ]
                        ),
                        html.P(
                            [
                                "As estimativas utilizam o peso amostral V1028 para obter valores representativos ",
                                "da população ocupada de Pernambuco em cada trimestre.",
                            ],
                            style={"marginTop": 10},
                        ),
                    ],
                    style={
                        "background": colors["card"],
                        "padding": 20,
                        "borderRadius": 8,
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                    },
                )
            ]
        )

    # Função auxiliar para montar 3 gráficos por trimestre
    def layout_three_charts(var1, var2, var3, title_prefix):
        # Agrega por trimestre somando sobre os CNAEs
        agg = (
            df.groupby("Trimestre", as_index=False)[[var1, var2, var3]]
            .sum(min_count=1)
        )
        # Recalcular médias agregadas, se desejar, ou manter a soma de médias por CNAE.
        # Aqui, para Renda Média_Total etc., é mais correto:
        if var1 == "n_ocup_pond" and var2 == "renda_total_pond" and var3 == "Renda Média_Total":
            agg["Renda Média_Total"] = agg["renda_total_pond"] / agg["n_ocup_pond"]
        if var1 == "n_empregador_pond" and var2 == "renda_empregador_pond" and var3 == "Renda Média_empregador":
            agg["Renda Média_empregador"] = agg["renda_empregador_pond"] / agg["n_empregador_pond"]
        if var1 == "n_conta_propria_pond" and var2 == "renda_conta_propria_pond" and var3 == "Renda Média_conta_propria":
            agg["Renda Média_conta_propria"] = agg["renda_conta_propria_pond"] / agg["n_conta_propria_pond"]

        fig1 = px.bar(
            agg,
            x="Trimestre",
            y=var1,
            title=f"{title_prefix} – {var1}",
            color="Trimestre",
        )
        fig2 = px.bar(
            agg,
            x="Trimestre",
            y=var2,
            title=f"{title_prefix} – {var2}",
            color="Trimestre",
        )
        fig3 = px.line(
            agg,
            x="Trimestre",
            y=var3,
            markers=True,
            title=f"{title_prefix} – {var3}",
        )

        return html.Div(
            [
                html.Div([dcc.Graph(figure=fig1)], style={"width": "32%", "display": "inline-block", "margin": "1%"}),
                html.Div([dcc.Graph(figure=fig2)], style={"width": "32%", "display": "inline-block", "margin": "1%"}),
                html.Div([dcc.Graph(figure=fig3)], style={"width": "32%", "display": "inline-block", "margin": "1%"}),
            ]
        )

    if tab == "total":
        return layout_three_charts(
            "n_ocup_pond",
            "renda_total_pond",
            "Renda Média_Total",
            "Total de Ocupados",
        )

    if tab == "empregador":
        return layout_three_charts(
            "n_empregador_pond",
            "renda_empregador_pond",
            "Renda Média_empregador",
            "Empregadores",
        )

    if tab == "conta_propria":
        return layout_three_charts(
            "n_conta_propria_pond",
            "renda_conta_propria_pond",
            "Renda Média_conta_propria",
            "Conta Própria",
        )

    return html.Div("Selecione uma aba.")

# --------------------------------------------
# Run
# --------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)