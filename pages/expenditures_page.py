import dash
from dash import html, dcc, callback, Input, Output
import duckdb as db
import plotly.express as px
import summarize_data as summ
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# create page for dash app
dash.register_page(__name__)

# show total population & employment + real gdp by state for each industry

# create DuckDB database
con = db.connect("db.bureau_economic_analysis.db", read_only=True)
summ_data = summ.summarize_bea(con)
change_rate_df = summ_data.summarize_ce_change_rate()

con.close()

# define app layout
layout = html.Div([
    html.Div(children="Consumer Expenditures", style={"color": "black", "fontSize": 26}),
    html.Br(),
    dcc.Graph(id="pie-app-change_rate-graph"),
    html.Br(),
])

# call back for pie chart
@callback(
    Output("pie-app-change_rate-graph", "figure"),
    # Input("bar-app-emp_state-dropdown", "value")
)
def update_bar_graph(year):
    change_rate_filtered = change_rate_df[change_rate_df.year == year]
    durable_goods = change_rate_filtered[change_rate_filtered.consumer_expenditure=="durable goods"]
    housing = change_rate_filtered[change_rate_filtered.consumer_expenditure=="housing"]
    nondurable_goods = change_rate_filtered[change_rate_filtered.consumer_expenditure=="nondurable goods"]
    services = change_rate_filtered[change_rate_filtered.consumer_expenditure=="services"]

    change_rate_pie = make_subplots(rows=2, cols=2, specs=[[{"type":"domain"}, {"type":"domain"}],
                                           [{"type":"domain"}, {"type":"domain"}]])
    
    change_rate_pie.add_trace(go.Pie(labels=durable_goods.change_rate.unique(), values=durable_goods.percent, name="Durable Goods"),
                1, 1)
    change_rate_pie.add_trace(go.Pie(labels=housing.change_rate.unique(), values=housing.percent, name="Housing"),
                1, 2)
    change_rate_pie.add_trace(go.Pie(labels=nondurable_goods.change_rate.unique(), values=nondurable_goods.percent, name="Nondurable Goods"),
                2, 1)
    change_rate_pie.add_trace(go.Pie(labels=services.change_rate.unique(), values=services.percent, name="Services"),
                2, 2)
    return change_rate_pie
