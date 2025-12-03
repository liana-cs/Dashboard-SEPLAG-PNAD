from dash import Input, Output, html, dcc
from dash.dependencies import ALL, MATCH

from styles import colors, card_style_base, tab_style, tab_selected_style
from components import layout_three_charts

def register_callbacks(app, df, anos_disponiveis, ano_default):
    # Título
    @app.callback(
        Output("titulo-dashboard", "children"),
        Input("tabs-top", "value"),
    )
    def update_titulo_dashboard(tab_top):
        return "PNAD Contínua – Ocupação e Renda em Pernambuco"

    # Conteúdo da aba de topo
    @app.callback(
        Output("tab-content-top", "children"),
        Input("tabs-top", "value"),
    )
    def render_tab_top(tab_top):
        if tab_top == "apresentacao":
            vars_info = [
                ("n_ocup_pond",
                 "Número de ocupados ponderado (soma dos pesos amostrais V1028 para todas as pessoas ocupadas)."),
                ("renda_total_pond",
                 "Soma ponderada da renda total do trabalho (trabalho principal + trabalho secundário + outros rendimentos de trabalho)."),
                ("Renda Média_Total",
                 "Renda média do trabalho para o total de ocupados (renda_total_pond / n_ocup_pond)."),
                ("n_empregador_pond",
                 "Número ponderado de empregadores (pessoas ocupadas na condição de empregador)."),
                ("renda_empregador_pond",
                 "Renda total ponderada do trabalho dos empregadores."),
                ("Renda Média_empregador",
                 "Renda média do trabalho dos empregadores (renda_empregador_pond / n_empregador_pond)."),
                ("n_conta_propria_pond",
                 "Número ponderado de trabalhadores por conta própria."),
                ("renda_conta_propria_pond",
                 "Renda total ponderada do trabalho dos trabalhadores por conta própria."),
                ("Renda Média_conta_propria",
                 "Renda média do trabalho dos conta própria (renda_conta_propria_pond / n_conta_propria_pond)."),
            ]

            info_card = html.Div(
                [
                    html.H2("Informações Gerais", style={"color": colors["primary"], "marginBottom": 10}),
                    html.P(
                        [
                            "Esta base apresenta indicadores trimestrais da ",
                            html.B("PNAD Contínua (IBGE)"),
                            " para o estado de Pernambuco (UF=26), ",
                            "focando a ocupação e a renda do trabalho.",
                        ]
                    ),
                    html.P(
                        [
                            "As informações estão organizadas em três grupos: ",
                            html.B("Total de Ocupados"),
                            ", ",
                            html.B("Empregadores"),
                            " e ",
                            html.B("Trabalhadores por Conta Própria"),
                            ", sempre por trimestre e ano.",
                        ]
                    ),
                ],
                style=card_style_base,
            )

            var_buttons = []
            for var_name, var_desc in vars_info:
                var_buttons.append(
                    html.Div(
                        [
                            html.Button(
                                var_name,
                                id={"type": "var-btn", "index": var_name},
                                n_clicks=0,
                                style={
                                    "width": "100%",
                                    "textAlign": "left",
                                    "padding": "10px 12px",
                                    "margin": "4px 0",
                                    "border": f"1px solid {colors['primary']}",
                                    "borderRadius": "6px",
                                    "background": "#ffffff",
                                    "color": colors["primary"],
                                    "fontWeight": "bold",
                                    "cursor": "pointer",
                                },
                            ),
                            html.Div(
                                var_desc,
                                id={"type": "var-desc", "index": var_name},
                                style={
                                    "display": "none",
                                    "padding": "8px 12px 12px 12px",
                                    "borderLeft": f"3px solid {colors['alert']}",
                                    "marginBottom": "4px",
                                    "backgroundColor": "#f9f9f9",
                                    "borderRadius": "0 0 6px 6px",
                                    "fontSize": "0.9rem",
                                },
                            ),
                        ]
                    )
                )

            vars_card = html.Div(
                [
                    html.H2("Definições das Variáveis", style={"color": colors["primary"], "marginBottom": 10}),
                    html.P(
                        "Clique em uma variável para visualizar a definição.",
                        style={"fontSize": "0.95rem", "color": "#555", "marginBottom": 12},
                    ),
                    html.Div(var_buttons),
                ],
                style=card_style_base,
            )

            return html.Div(
                [
                    html.Div(info_card, style={"width": "100%"}),
                    html.Div(vars_card, style={"width": "100%"}),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "stretch",
                    "marginTop": 20,
                    "gap": "20px",
                    "maxWidth": "900px",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                },
            )

        # Aba "Módulos"
        return html.Div(
            [
                dcc.Tabs(
                    id="tabs-modulo",
                    value="total",
                    children=[
                        dcc.Tab(label="Total de Ocupados", value="total", style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label="Empregadores", value="empregador", style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label="Conta Própria", value="conta_propria", style=tab_style, selected_style=tab_selected_style),
                    ],
                ),
                html.Div(
                    [
                        html.Label(
                            "Ano",
                            style={
                                "fontWeight": "bold",
                                "marginRight": "8px",
                                "color": colors["primary"],
                            },
                        ),
                        dcc.Dropdown(
                            id="filter-ano",
                            options=[{"label": str(a), "value": int(a)} for a in anos_disponiveis],
                            value=ano_default,
                            clearable=False,
                            style={"width": "180px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "10px",
                        "padding": "12px 0 8px 0",
                    },
                ),
                html.Div(id="tab-content-modulo"),
            ]
        )

    # Conteúdo dos módulos
    @app.callback(
        Output("tab-content-modulo", "children"),
        Input("tabs-modulo", "value"),
        Input("filter-ano", "value"),
    )
    def render_modulo(tab_mod, ano_sel):
        if ano_sel is None:
            dff = df.copy()
        else:
            dff = df[df["Ano"] == ano_sel].copy()

        if tab_mod == "total":
            return layout_three_charts(dff, "n_ocup_pond", "renda_total_pond",
                                       "Renda Média_Total", "Total de Ocupados")
        if tab_mod == "empregador":
            return layout_three_charts(dff, "n_empregador_pond", "renda_empregador_pond",
                                       "Renda Média_empregador", "Empregadores")
        if tab_mod == "conta_propria":
            return layout_three_charts(dff, "n_conta_propria_pond", "renda_conta_propria_pond",
                                       "Renda Média_conta_propria", "Trabalhadores por Conta Própria")
        return html.Div("Selecione um módulo.")

    # Abrir/fechar descrições
    @app.callback(
        Output({"type": "var-desc", "index": MATCH}, "style"),
        Output({"type": "var-btn", "index": MATCH}, "style"),
        Input({"type": "var-btn", "index": MATCH}, "n_clicks"),
        Input({"type": "var-btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_var_description(n_clicks_this, all_clicks):
        base_btn_style = {
            "width": "100%",
            "textAlign": "left",
            "padding": "10px 12px",
            "margin": "4px 0",
            "border": f"1px solid {colors['primary']}",
            "borderRadius": "6px",
            "background": "#ffffff",
            "color": colors["primary"],
            "fontWeight": "bold",
            "cursor": "pointer",
        }

        desc_style_closed = {
            "display": "none",
            "padding": "8px 12px 12px 12px",
            "borderLeft": f"3px solid {colors['alert']}",
            "marginBottom": "4px",
            "backgroundColor": "#f9f9f9",
            "borderRadius": "0 0 6px 6px",
            "fontSize": "0.9rem",
        }

        desc_style_open = desc_style_closed.copy()
        desc_style_open["display"] = "block"

        if n_clicks_this is None:
            return desc_style_closed, base_btn_style

        if n_clicks_this % 2 == 1:
            btn_style_open = base_btn_style.copy()
            btn_style_open.update(
                {
                    "background": colors["primary"],
                    "color": "#ffffff",
                }
            )
            return desc_style_open, btn_style_open
        else:
            return desc_style_closed, base_btn_style