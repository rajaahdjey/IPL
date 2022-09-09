import dash
from dash import html
from dash import dcc
from dash.dependencies import Output,Input
from matplotlib.pyplot import figure
import plotly.express as px
import pandas as pd
import numpy as np
import os
from player_filter import *

#adapted from : https://stackoverflow.com/questions/59253961/pass-dash-dropdown-selection-to-variable

df, players = load_data()

player_name="MS Dhoni"

def generate_dfs(player_name = player_name):
    chart_df_pp_bowl,\
    chart_df_mid_bowl,\
    chart_df_death_bowl,\
    chart_df_pp_style,\
    chart_df_mid_style,\
    chart_df_death_style = player_charting(player=player_name)

    return chart_df_pp_bowl,chart_df_mid_bowl,chart_df_death_bowl,\
        chart_df_pp_style,chart_df_mid_style,chart_df_death_style,player_name

app = dash.Dash(__name__)
app.title = "IPL Head to Head Dashboard"

app.layout = html.Div(children=[
    # New Div for menu area
    html.Div(
        id='menu_area',
        children=[
            html.H1("IPL - Matchups Explorer"),
            html.P(f"Data from 2008 to {max(df.season.unique())}"),
            html.Div(
                className="menu_title",
                children="Select Player Name - Search with lastnames eg., Kohli"
            ),
            dcc.Dropdown(
                id="player_filter",
                className="dropdown",
                options=[{"label": x, "value": x}
                         for x in df["striker"].unique()],
                clearable=False,
                value="MS Dhoni"
            ),
     html.Div(id='table-container',children=[]),
        ]
    )
])

#create functions to return graphs

def generate_graphs(chart_df_pp_bowl,chart_df_mid_bowl,chart_df_death_bowl,\
        chart_df_pp_style,chart_df_mid_style,chart_df_death_style,player_name):
    return dcc.Graph(
            id='graph_pp_bowl',
            figure=  px.bar(chart_df_pp_bowl[0:20], x="unique_name",
                   y="strike_rate", color='bowling_style', title=f"{player_name} : Bowler matchups in the Powerplay")
        ), dcc.Graph(
            id='graph2',
            figure=  px.bar(chart_df_pp_style, x="bowling_style",
                   y="strike_rate",  title=f"{player_name} : Bowling Style matchups in the Powerplay")
        ), dcc.Graph(
            id='graph3',
            figure=  px.bar(chart_df_mid_bowl[0:20], x="unique_name",
                   y="strike_rate", color='bowling_style', title=f"{player_name} : Bowler matchups in overs 7 to 15")
        ), dcc.Graph(
            id='graph4',
            figure=  px.bar(chart_df_mid_style, x="bowling_style",
                   y="strike_rate",  title=f"{player_name} : Bowling Style matchups in overs 7 to 15")
        ), dcc.Graph(
            id='graph5',
            figure=  px.bar(chart_df_death_bowl[0:20], x="unique_name",
                   y="strike_rate", color='bowling_style', title=f"{player_name} : Bowler matchups in the death overs")
        ), dcc.Graph(
            id='graph6',
            figure=  px.bar(chart_df_death_style, x="bowling_style",
                   y="strike_rate",  title=f"{player_name} : Bowling Style matchups in the death overs")
        )

#add callback after layout sections

@app.callback(
    Output('table-container', component_property = 'children'),
    Input('player_filter',"value")
)

def update_chart(value):
    player = value
    df1,df2,df3,df4,df5,df6,filter = generate_dfs(player)
    return generate_graphs(df1,df2,df3,df4,df5,df6,filter)

if __name__ == "__main__":
    app.run_server(debug=True)