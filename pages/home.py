import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div([
    html.H1("Title"),
    html.Div([
        "Intro, motivation, and summary, img?"
    ])
])