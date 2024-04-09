import dash
from dash import html
import base64

dash.register_page(__name__, path="/")

# BEA image of Home page header
image_path = "pages/assets/bea.png"
test_base64 = base64.b64encode(open(image_path, "rb").read()).decode("ascii")

# define page layout
layout = html.Div([
    html.Br(),
    html.Img(src='data:image/png;base64,{}'.format(test_base64),
             style={"height":"50%", "width":"60%"}),
    html.H1("Intro"),
    html.Div([
        """
        The Bureau of Economic Analysis (BEA) is an agency within the U.S. Department of Commerce that is responsible for producing economic statistics. 
        It provides a wide range of data and analysis related to the U.S. economy. This dashboard will include US data on real GDP, population, employment,
        income, and consumer expenditures.
        """
    ]),
    html.H1("Data"),
    html.H4("Real GDP"),
    html.Div([
        """
        Real Gross Domestic Product is the measure of all goods & services produced by the state after adjusting for inflation. Due to taking into account 
        changes in price, real GDP is considered a more accurate measure of a state's economy. We'll be comparing annual real GDP growth for all 50 states
        + DC.
        """
    ]),
    html.H4("Population & Employment"),
    html.Div([
        """
        Each state's annual population and employment growth will be compared to provide context into labor supply. Paired with real GDP, the Population page 
        will show show both population and employment growth follows trends with various real GDP indsutries. 
        """
    ]),
    html.H4("Income"),
    html.Div([
        """
        Income is displayed in two types; personal income & disposable income. Peronsal income is the total income received by individuals from all sources 
        before taxes and deductions. Disposable income is the amount of personal income left after subtracting taxes and other deductions. We'll be highlighting the
        top 5 state income increases by year, in addition to a comparison in income between states.
        """
    ]),
    html.H4("Consumer Expenditures"),
    html.Div([
        """
        Consumer Expenditures are a measure of the total amount of money spent by households on goods and services. As a key component to GDP, consumer 
        expenditures are valuable in understanding the economy. Consumer expenditures encompass a range of topics, here we will focus on durable goods, nondurable
        goods, services, and housing. 
        """
    ]),
    html.H1("References"),
    html.H1("Requests"),
])