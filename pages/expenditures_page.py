import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import duckdb as db
import plotly.express as px
import summarize_data as summ
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_ag_grid as dag

# create page for dash app
dash.register_page(__name__)

# create DuckDB database
con = db.connect("db.bureau_economic_analysis.db", read_only=True)
summ_data = summ.summarize_bea(con)
change_rate_summ_df = summ_data.summarize_ce_change_rate()
change_rate_df = summ_data.ce_change_rate_table()

con.close()

ce_year = dcc.Dropdown(
    id="pie-app-change_rate-dropdown",
    options = change_rate_summ_df.year.sort_values().unique(),
    value="2022",
    clearable=False,
    style={"width": "150px"}

)
# define app layout
layout = html.Div([
    html.Br(),
    html.Div(children="US Consumer Expenditures", style={"color": "black", "fontSize": 26}),
    html.Div(children="Durable Goods, Nondurable goods, Housing, & Services", style={"color": "black", "fontSize": 18}),
    html.Br(),
    html.P("Select year:"),
    dbc.Col(ce_year, lg=6, sm=12),
    dbc.Row(
        [   
            dbc.Col(dcc.Graph(id="pie-app-change_rate-graph"), width=5),
            dbc.Col(dash_table.DataTable(id="pie-app-datatable", page_size=20), 
                    style={"width": "50%", 
                           "display": "inline-block"}),
        ], style={"display": "flex"}
    ),
    html.Br(),
])

# call back for pie chart
@callback(
    Output("pie-app-change_rate-graph", "figure"),
    Input("pie-app-change_rate-dropdown", "value")
)
def update_pie_charts(year):
    change_rate_summ_filtered = change_rate_summ_df[change_rate_summ_df.year == year]
    durable_goods = change_rate_summ_filtered[change_rate_summ_filtered.consumer_expenditure=="durable goods"]
    housing = change_rate_summ_filtered[change_rate_summ_filtered.consumer_expenditure=="housing"]
    nondurable_goods = change_rate_summ_filtered[change_rate_summ_filtered.consumer_expenditure=="nondurable goods"]
    services = change_rate_summ_filtered[change_rate_summ_filtered.consumer_expenditure=="services"]

    change_rate_pie = make_subplots(
                        rows=2, 
                        cols=2, 
                        specs=[[{"type":"domain"}, 
                                {"type":"domain"}],
                               [{"type":"domain"}, 
                                {"type":"domain"}]],
                        subplot_titles = ("Durable Goods", "Housing", "Nondurable Goods", "Services"))

    change_rate_pie.add_trace(
        go.Pie(labels=durable_goods.change_rate.unique(), 
               values=durable_goods.percent, 
               name="Durable Goods"),
               1, 1)
    change_rate_pie.add_trace(
        go.Pie(labels=housing.change_rate.unique(), 
               values=housing.percent, 
               name="Housing"),
               1, 2)
    change_rate_pie.add_trace(
        go.Pie(labels=nondurable_goods.change_rate.unique(), 
               values=nondurable_goods.percent, 
               name="Nondurable Goods"),
               2, 1)
    change_rate_pie.add_trace(
        go.Pie(labels=services.change_rate.unique(), 
               values=services.percent, 
               name="Services"),
               2, 2)

    change_rate_pie.update_layout(height=700,
                    width=700,
                    title_text="Change rate from previous year",
                    title_x=0.5,
                    title_font_size=24)

    for i in change_rate_pie["layout"]["annotations"]:
        i["font"] = dict(size=14)
    return change_rate_pie

# call back for datatable
@callback(
    Output("pie-app-datatable", "data"),
    Input("pie-app-change_rate-dropdown", "value")
)
def update_datatable(year):
    change_rate_df_filtered = change_rate_df[change_rate_df.year == year]
    datatable = change_rate_df_filtered.to_dict("records")
    return datatable