import dash
from dash import html, dcc, callback, Input, Output
import duckdb as db
import plotly.express as px
import summarize_data as summ

# create page for dash app
dash.register_page(__name__)

# show total population & employment + real gdp by state for each industry

# create DuckDB database
con = db.connect("db.bureau_economic_analysis.db", read_only=True)
summ_data = summ.summarize_bea(con)
employment_population_df = summ_data.create_employment_population()
real_gdp_df = summ_data.create_real_gdp()

con.close()

emp_state_list = sorted(employment_population_df.state.unique())
gdp_state_list = sorted(real_gdp_df.state.unique())
gdp_industries = sorted(real_gdp_df.industry.unique())

# define app layout
layout = html.Div([
    html.Div(children="Bureau Of Economic Analysis Dashboard", style={"color": "black", "fontSize": 26}),
    html.Br(),
    dcc.Dropdown(
        id="bar-app-emp_state-dropdown",
        value=["New York", "California", "Texas", "Florida", "Illinois", "Colorado", "Massachusetts"], # default value
        options=emp_state_list, # all options
        multi=True,
        ),
    dcc.Graph(id="bar-app-employment-graph"),
    html.Br(),
    dcc.Dropdown(
        id="line-app-gdp_industry-dropdown",
        value="All industry total",
        options=gdp_industries,
        multi=False,
        ),
    dcc.Dropdown(
        id="line-app-gdp_state-dropdown",
        value=["New York", "California"],
        options=gdp_state_list,
        multi=True,
        ),
    dcc.Graph(id="line-app-realgdp-graph")
])

# call back for bar chart
@callback(
    Output("bar-app-employment-graph", "figure"),
    Input("bar-app-emp_state-dropdown", "value")
)
def update_bar_graph(state):
    employment_population_filtered = employment_population_df[employment_population_df["state"].isin(state)]
    employment_pop_bar = px.bar(employment_population_filtered,
                                x="state", 
                                y=["population", "employment"], 
                                animation_frame="year", 
                                barmode="group",
                                title="State population & employment 2017-2022",
                                width=1350, 
                                height=600,
                                labels={"value": "# of individuals",
                                        "year": "Year"})
    return employment_pop_bar

# call back for line chart 
@callback(
    Output("line-app-realgdp-graph", "figure"),
    Input("line-app-gdp_industry-dropdown", "value"),
    Input("line-app-gdp_state-dropdown", "value")
)
def update_line_graph(industry, state):
    real_gdp_filtered = real_gdp_df[(real_gdp_df["state"].isin(state)) & (real_gdp_df["industry"]==industry)]
    real_gdp_line = px.line(real_gdp_filtered, 
                            x="year", 
                            y="real_gdp_million",
                            color="state",
                            title="State real GDP by industry 2017-2022",
                            width=1350, 
                            height=600,
                            labels={"real_gdp_million": "Real GDP (in millions)",
                                    "year": "Year"})
    
    # change line color; bars are already red and blue
    return real_gdp_line