from dash import Input, Output, html, dcc
from dash.dependencies import ALL, MATCH
import plotly.express as px 

from styles import colors, card_style_base, tab_style, tab_selected_style

def register_callbacks(app, df, anos_disponiveis, ano_default):
    # Título
    @app.callback(
        Output("titulo-dashboard", "children"),
        Input("tabs-top", "value"),
    )
    def update_titulo_dashboard(tab_top):
        return "PNAD Contínua – Ocupação e Renda em Pernambuco"

    # aba de topo
    @app.callback(
        Output("tab-content-top", "children"),
        Input("tabs-top", "value"),
    )
    def render_tab_top(tab_top):
        if tab_top == "apresentacao":
            vars_info = [
                ("Número de ocupados",
                 "Número de ocupados ponderado, representado pela variável 'n_ocup_pond'."),
                ("Renda total do trabalho",
                 "Soma ponderada da renda total do trabalho (trabalho principal + trabalho secundário + outros rendimentos de trabalho), representado pela variável 'renda_total_pond'."),
                ("Renda Média Total",
                 "Renda média do trabalho para o total de ocupados (renda_total_pond / n_ocup_pond), representado pela variável Renda_Média_Total."),
                ("Número de empregadores ",
                 "Número ponderado de empregadores (pessoas ocupadas na condição de empregador), representado pela variável 'n_empregador_pond'."),
                ("Renda total do trabalho dos empregadores",
                 "Renda total ponderada do trabalho dos empregadores, representado pela variável 'renda_empregador_pond'."),
                ("Renda média do trabalho dos empregadores",
                 "Renda média do trabalho dos empregadores (renda_empregador_pond / n_empregador_pond), representado pela variável 'Renda_Média_empregador."),
                ("Número de trabalhadores por conta própria",
                 "Número ponderado de trabalhadores por conta própria, representado pela variável 'n_conta_propria_pond'."),
                ("Renda total do trabalho dos trabalhadores por conta própria",
                 "Renda total ponderada do trabalho dos trabalhadores por conta própria, representado pela variável 'renda_conta_propria_pond'."),
                ("Renda Média de trabalhadores por conta própria",
                 "Renda média do trabalho dos conta própria (renda_conta_propria_pond / n_conta_propria_pond), representado pela variável 'Renda_Média_conta_propria'."),
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

        # "Módulos"
        return html.Div(
        [
            # abas internas 
            dcc.Tabs(
                id="tabs-modulo",
                value="total",
                children=[
                    dcc.Tab(
                        label="Total de Ocupados",
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

            # filtros 
            html.Div(
                [
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
                                options=(
                                    [{"label": "Todos os anos", "value": "Todos"}] +
                                    [{"label": str(a), "value": int(a)} for a in anos_disponiveis]
                                ),
                                value="Todos",          
                                clearable=False,
                                style={"width": "200px"},
                            ),

                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Tipo de gráfico",
                                style={
                                    "fontWeight": "bold",
                                    "marginRight": "8px",
                                    "color": colors["primary"],
                                },
                            ),
                            dcc.Dropdown(
                                id="filter-grafico",
                                options=[
                                    {"label": "Quantidade (n_ocup_pond)", "value": "qtd"},
                                    {"label": "Renda Total (renda_total_pond)", "value": "renda_total"},
                                    {"label": "Renda Média (Renda_Média_total)", "value": "renda_media"},
                                ],
                                value="qtd",
                                clearable=False,
                                style={"width": "260px"},
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "justifyContent": "flex-start",
                    "gap": "20px",
                    "padding": "12px 0 12px 0",
                },
            ),

            html.Div(id="tab-content-modulo"),
        ]
    )

    @app.callback(
        Output("tab-content-modulo", "children"),
        Input("tabs-modulo", "value"),
        Input("filter-ano", "value"),
        Input("filter-grafico", "value"),
    )
    def render_modulo(tab_mod, ano_sel, tipo_grafico):
        if ano_sel in (None, "Todos"):
            dff = df.copy()
        else:
            dff = df[df["Ano"] == ano_sel].copy()

        if tab_mod == "total":
            col_qtd   = "n_ocup_pond"
            col_rtot  = "renda_total_pond"
            col_rmed  = "Renda Média_Total"
            titulo_mod = "Total de Ocupados"
        elif tab_mod == "empregador":
            col_qtd   = "n_empregador_pond"
            col_rtot  = "renda_empregador_pond"
            col_rmed  = "Renda Média_empregador"
            titulo_mod = "Empregadores"
        else:  
            col_qtd   = "n_conta_propria_pond"
            col_rtot  = "renda_conta_propria_pond"
            col_rmed  = "Renda Média_conta_propria"
            titulo_mod = "Trabalhadores por Conta Própria"

        if tipo_grafico == "qtd":
            y_col = col_qtd
            y_label = col_qtd
            titulo = f"{titulo_mod} – Quantidade"
            modo = "qtd"
        elif tipo_grafico == "renda_total":
            y_col = col_rtot
            y_label = col_rtot
            titulo = f"{titulo_mod} – Renda Total"
            modo = "renda_total"
        else:  
            y_col = col_rmed
            y_label = col_rmed
            titulo = f"{titulo_mod} – Renda Média"
            modo = "renda_media"

        if modo == "qtd":
            fig = px.bar(
                dff,
                x="Periodo",
                y=y_col,
                title=titulo,
            )
            fig.update_traces(marker_color=colors["primary"])
            fig.update_yaxes(tickformat="~s")

        elif modo == "renda_total":
            fig = px.bar(
                dff,
                x="Periodo",
                y=y_col,
                title=titulo,
            )
            fig.update_traces(marker_color=colors["accent"])

            y_vals = dff[y_col].dropna().to_numpy()
            if y_vals.size > 0:
                y_min = float(y_vals.min())
                y_max = float(y_vals.max())

                n_ticks = 5
                y_start = 0.0
                step = (y_max - y_start) / (n_ticks - 1) if n_ticks > 1 else y_max or 1.0
                tick_vals = [y_start + i * step for i in range(n_ticks)]

                def fmt_bmk(v):
                    v = float(v)
                    sign = "-" if v < 0 else ""
                    v_abs = abs(v)
                    if v_abs >= 1e9:
                        return f"{sign}R$ {v_abs/1e9:.1f}B"
                    elif v_abs >= 1e6:
                        return f"{sign}R$ {v_abs/1e6:.1f}M"
                    elif v_abs >= 1e3:
                        return f"{sign}R$ {v_abs/1e3:.1f}K"
                    else:
                        return f"{sign}R$ {v_abs:.0f}"

                tick_text = [fmt_bmk(v) for v in tick_vals]
                fig.update_yaxes(tickvals=tick_vals, ticktext=tick_text)
            else:
                fig.update_yaxes(tickprefix="R$ ", tickformat=".0f")

        else:  
            fig = px.line(
                dff,
                x="Periodo",
                y=y_col,
                markers=True,
                title=titulo,
            )
            fig.update_traces(
                line=dict(color=colors["secondary"], width=3),
                marker=dict(color=colors["accent"], size=8),
            )
            fig.update_yaxes(tickformat=".0f", separatethousands=True, tickprefix="R$ ", rangemode="tozero")

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            title_x=0.5,
            title_font=dict(size=18, color=colors["primary"]),
            margin=dict(t=80, l=60, r=40, b=60),
            plot_bgcolor="#ffffff",
            paper_bgcolor=colors["card"],
            height=450,
        )
        fig.update_xaxes(showgrid=False, linecolor="#cccccc")
        fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0")

        card = html.Div(
            dcc.Graph(figure=fig),
            style={
                "width": "auto",
                "backgroundColor": colors["card"],
                "borderRadius": "12px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                "padding": "8px",
                "overflow": "hidden",
                "marginRight": "auto",
            },
        )

        return card

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