from dash import dcc, html
from styles import colors, tab_style, tab_selected_style

def make_layout():
    return html.Div(
        [
            html.Div(
                [
                    # Header
                    html.Div(
                        [
                            html.Img(
                                src="/assets/logo-ifpe-branco.png",
                                style={
                                    "height": "40px",
                                    "marginLeft": "20px",
                                    "marginRight": "20px",
                                },
                            ),
                            html.H1(
                                id="titulo-dashboard",
                                style={
                                    "flex": "1",
                                    "textAlign": "center",
                                    "color": "#f6f6f6",
                                    "margin": 0,
                                    "padding": "16px 0",
                                },
                            ),
                            html.Div(
                                style={
                                    "width": "60px",
                                    "marginRight": "20px",
                                }
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "space-between",
                            "background": (
                                f"linear-gradient(90deg, {colors['primary']} 0%, "
                                f"{colors['secondary']} 50%, {colors['accent']} 100%)"
                            ),
                            "borderTopLeftRadius": "16px",
                            "borderTopRightRadius": "16px",
                        },
                    ),
                    # Abas de topo
                    dcc.Tabs(
                        id="tabs-top",
                        value="apresentacao",
                        children=[
                            dcc.Tab(
                                label="Apresentação",
                                value="apresentacao",
                                style=tab_style,
                                selected_style=tab_selected_style,
                            ),
                            dcc.Tab(
                                label="Módulos",
                                value="modulos",
                                style=tab_style,
                                selected_style=tab_selected_style,
                            ),
                        ],
                    ),
                    html.Div(id="tab-content-top", style={"padding": "20px"}),
                ],
                style={
                    "backgroundColor": colors["card"],
                    "borderRadius": "16px",
                    "boxShadow": "0 3px 8px rgba(0,0,0,0.15)",
                    "maxWidth": "1100px",
                    "width": "100%",
                    "margin": "0 auto",
                },
            ),
        ],
        style={
            "backgroundColor": colors["background"],
            "minHeight": "100vh",
            "padding": 20,
        },
    )