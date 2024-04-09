import dash
from dash import html
import base64

dash.register_page(__name__, path="/")

image_path = "pages/assets/bea.png"
test_base64 = base64.b64encode(open(image_path, "rb").read()).decode("ascii")

layout = html.Div([
    html.Br(),
    html.Img(src='data:image/png;base64,{}'.format(test_base64),
             style={"height":"50%", "width":"60%"}),
    html.H1("Intro"),
    html.Div([
        """
        The Bureau of Economic Analysis (BEA) is an agency within the U.S. Department of Commerce that is responsible for producing economic statistics. 
        It provides a wide range of data and analysis related to the U.S. economy. This dashboard will include US data on Real GDP, population, employment,
        income, wages, and consumer expenditures.
        """
    ]),
    html.H1("Data"),
    html.H4("Real GDP"),
    html.Div([
        """
        Something
        """
    ]),
    html.H4("Population"),
    html.Div([
        """
        Something
        """
    ]),
    html.H4("Employment"),
    html.Div([
        """
        Something
        """
    ]),
    html.H4("Income/Wages"),
    html.Div([
        """
        Something
        """
    ]),
    html.H4("Consumer Expenditures"),
    html.Div([
        """
        Something
        """
    ]),
    html.H1("References"),
    html.H1("Requests"),
])