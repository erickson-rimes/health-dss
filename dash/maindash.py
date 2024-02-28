import dash
import dash_bootstrap_components as dbc
import pandas as pd

my_app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.MATERIA, dbc.icons.FONT_AWESOME],
)
my_app.title = "Health DSS"
server = my_app.server

# import the dataset
url = "../data/train.json"
df = pd.read_json(url)