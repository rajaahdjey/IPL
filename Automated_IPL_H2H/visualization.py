import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
import numpy as np
import os

#read in data

cwd = os.getcwd()
df = pd.read_csv(cwd+"/data/all_matches.csv", dtype={
                 'match_id': 'int', 'season': 'str', 'innings': 'int', 'ball': 'float'}, parse_dates=True)
df.season = df.season.replace(
    {"2007/08": "2008", "2009/10": "2010", "2020/21": "2020"})

players = pd.read_csv("player_details.csv")

# basis dataframe

consolidated_df = pd.DataFrame()
consolidated_df = df.groupby(["striker"])["runs_off_bat"].agg(
    balls_faced="count", runs_total="sum").reset_index().sort_values(by="runs_total", ascending=False)

# create a plotly figure for use by dcc.Graph()

fig = px.bar(consolidated_df[0:20], x="striker",
              y="runs_total", title="Top 20 IPL runscorers of all time")

fig.update_layout(
    template="ggplot2"
)

app = dash.Dash(__name__)
app.title = "IPL Dashboard"

app.layout = html.Div(
    id="app-container",
    children=[html.H1("Top 20 IPL runscorers of all time"),
              html.P("From 2008 - 2022 , total 910 matches"),
              dcc.Graph(figure=fig)
              ]

)


if __name__ == "__main__":
    app.run_server(debug=True)
