import warnings
import dash

from data_loader import load_data
from styles import colors
from layout import make_layout
from callbacks import register_callbacks

warnings.filterwarnings("ignore")

df = load_data()
anos_disponiveis = sorted(df["Ano"].dropna().unique().tolist())
ano_default = anos_disponiveis[0] if anos_disponiveis else None

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="PNAD – Ocupação e Renda",
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = make_layout()

register_callbacks(app, df, anos_disponiveis, ano_default)

if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)