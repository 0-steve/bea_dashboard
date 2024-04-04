import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import duckdb as db
import plotly.express as px
import summarize_data as summ

# create page for dash app
dash.register_page(__name__)

# create DuckDB database
con = db.connect("db.bureau_economic_analysis.db", read_only=True)
summ_data = summ.summarize_bea(con)
income_df = summ_data.income_top_five()
income_type_df = summ_data.income_type_comparison()

con.close()

income_state_list = sorted(income_df.state.unique())

# income compare toggles
dropdown_state_a = dcc.Dropdown(
    id="income_compare_state-a",
    options=income_type_df.state.unique(),
    value="New York",
)

dropdown_state_b = dcc.Dropdown(
    id="income_compare_state-b",
    options=income_type_df.state.unique(),
    value="California",
)

info_card = dbc.Card(
    dbc.CardBody(
        html.P("Choose two states to compare")
        )
    )

# income toggles
income_type_option = dcc.RadioItems(
    id="bar-app-income_type-select",
    options=["personal income", "disposable income"],
    value="personal income", # default
    inline=True,
)

income_year = dcc.Dropdown(
    id="bar-app-income_year-dropdown",
    options=income_df.year.unique(),
    value=2022,
    clearable=False,
    style={"width": "150px"}

)
# define app layout
layout = html.Div([
    html.Br(),
    html.Div(children="Personal and disposable income", style={"color": "black", "fontSize": 26}),
    html.Br(),
    dbc.Row(
        [dbc.Col(
            [
                html.P("Choose income type:"),
                dbc.Col(income_type_option, lg=6, sm=12),
                html.P("Select year:"),
                dbc.Col(income_year, lg=6, sm=12),
            ])
    ]),
    dcc.Graph(id="bar-app-income-graph"),
    html.Br(),
    dbc.Row(
        [
            dbc.Col([dropdown_state_a, dropdown_state_b], lg=6, sm=12),
            dbc.Col(info_card, lg=6, sm=12),
        ]
    ),
    dcc.Graph(id="scatter-app-income-graph"),
])

# call back for bar chart
@callback(
    Output("bar-app-income-graph", "figure"),
    Input("bar-app-income_year-dropdown", "value"),
    Input("bar-app-income_type-select", "value")
)
def update_bar_graph(year, income_type):

    income_filtered = income_df[(income_df.year==year) & (income_df.income_type==income_type)].sort_values("change_rank", ascending=False)
    income_h_bar = px.bar(income_filtered, 
                        x="income_change", 
                        y="year",
                        color="state", 
                        barmode="group",
                        orientation="h",
                        title="Top 5 personal/disposable income increases",
                        text=[f"{i}%" for i in income_filtered.income_change],
                        width=1350, 
                        height=600,
                        labels={"income_change": "Income change %",
                                "year": ""}
    )
    return income_h_bar

# call back for scatter 
@callback(
    Output("scatter-app-income-graph", "figure"),
    Input("income_compare_state-a", "value"),
    Input("income_compare_state-b", "value")
)
def update_line_graph(state1, state2):
    income_type_df_filtered = income_type_df[(income_type_df.state.isin([state1, state2]))].sort_values(["year","state"])
    income_type_scatter = px.scatter(income_type_df_filtered,
                                    x="personal_income",
                                    y="disposable_income",
                                    color="state",
                                    hover_data=["year"],
                                    title="Personal/Disposable income state comparison",
                                    width=1350, 
                                    height=600,
                                    labels={"personal_income": "Personal Income",
                                            "disposable_income": "Disposable Income"})
    return income_type_scatter