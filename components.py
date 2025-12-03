import plotly.express as px
from dash import html, dcc

from styles import colors 

def layout_three_charts(df_plot, var1, var2, var3, title_prefix):
    # Quantidade
    fig1 = px.bar(
        df_plot,
        x="Periodo",
        y=var1,
        title=f"{var1}",
        color="Periodo",
        color_discrete_sequence=[colors["primary"], colors["secondary"],
                                 colors["accent"], colors["primary"]],
    )
    fig1.update_layout(
        showlegend=True,
        xaxis_title="Período",
        yaxis_title=var1,
        title_x=0.5,
        title_font=dict(size=16, color=colors["primary"]),
        margin=dict(t=80, l=40, r=40, b=40),
        plot_bgcolor="#ffffff",
        paper_bgcolor=colors["card"],
        height=400,
    )
    fig1.update_xaxes(showgrid=False, linecolor="#cccccc")
    fig1.update_yaxes(showgrid=True, gridcolor="#e0e0e0",
                      tickformat=".0f", separatethousands=True)

    # Renda total
    fig2 = px.bar(
        df_plot,
        x="Periodo",
        y=var2,
        title=f"{var2}",
        color="Periodo",
        color_discrete_sequence=[colors["alert"], colors["secondary"],
                                 colors["accent"], colors["alert"]],
    )
    fig2.update_layout(
        showlegend=True,
        xaxis_title="Período",
        yaxis_title=var2,
        title_x=0.5,
        title_font=dict(size=16, color=colors["primary"]),
        margin=dict(t=80, l=40, r=40, b=40),
        plot_bgcolor="#ffffff",
        paper_bgcolor=colors["card"],
        height=400,
    )
    fig2.update_xaxes(showgrid=False, linecolor="#cccccc")
    fig2.update_yaxes(showgrid=True, gridcolor="#e0e0e0",
                      tickformat=".0f", separatethousands=True,
                      tickprefix="R$ ")

    # Renda média
    fig3 = px.line(
        df_plot,
        x="Periodo",
        y=var3,
        markers=True,
        title=f"{var3}",
    )
    fig3.update_traces(line=dict(color=colors["secondary"], width=3),
                       marker=dict(color=colors["accent"], size=8))
    fig3.update_layout(
        showlegend=True,
        xaxis_title="Período",
        yaxis_title=var3,
        title_x=0.5,
        title_font=dict(size=16, color=colors["primary"]),
        margin=dict(t=80, l=40, r=40, b=40),
        plot_bgcolor="#ffffff",
        paper_bgcolor=colors["card"],
        
    )
    fig3.update_xaxes(showgrid=False, linecolor="#cccccc")
    fig3.update_yaxes(showgrid=True, gridcolor="#e0e0e0",
                      tickformat=".0f", separatethousands=True,
                      tickprefix="R$ ")

    return html.Div(
        [
            html.Div(
                dcc.Graph(figure=fig1),
                style={
                    "flex": "1",
                    "margin": "0 8px",
                    "backgroundColor": colors["card"],
                    "borderRadius": "12px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "8px",
                    "overflow": "hidden",
                },
            ),
            html.Div(
                dcc.Graph(figure=fig2),
                style={
                    "flex": "1",
                    "margin": "0 8px",
                    "backgroundColor": colors["card"],
                    "borderRadius": "12px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "8px",
                    "overflow": "hidden",
                },
            ),
            html.Div(
                dcc.Graph(figure=fig3),
                style={
                    "flex": "1",
                    "margin": "0 8px",
                    "backgroundColor": colors["card"],
                    "borderRadius": "12px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "8px",
                    "overflow": "hidden",
                },
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "space-between",
            "marginTop": "24px",
        },
    )