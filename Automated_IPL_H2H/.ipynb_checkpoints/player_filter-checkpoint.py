def over_filter(df,min_over=1,max_over=20):
    temp_df = df[(df['ball']>(min_over-1)) & (df['ball']<=max_over)]
    return temp_df

def h2h_filter(df_filt,player_df,batsman="MS Dhoni"):
    df_batsman = df_filt[df_filt['striker'] == batsman]
    df_batsman = df_batsman[df_batsman["wides"].isna()]
    bat_h2h = df_batsman.groupby(['bowler'])["runs_off_bat"].agg(balls_faced="count",runs_total="sum").reset_index()
    bat_h2h["dismissals"] = df_batsman.groupby(['bowler'])["player_dismissed"].agg(balls_faced="count",dismissals="count").reset_index()["dismissals"]
    bat_h2h.sort_values(by = 'balls_faced',inplace=True,ascending=False)
    bat_h2h.rename({'bowler':'unique_name'},axis=1,inplace=True)
    bat_h2h_bowl = bat_h2h.merge(player_df,how='left',on='unique_name').drop(columns=['team','identifier','key_cricinfo','batting_style','name','player_type','season','Unnamed: 0'])
    bat_h2h_bowl.drop_duplicates(inplace=True)
    bat_h2h_bowl["strike_rate"] = (bat_h2h_bowl["runs_total"]*100/bat_h2h_bowl["balls_faced"])
    bat_h2h_bowl["balls_per_out"] = (bat_h2h_bowl["balls_faced"]/bat_h2h_bowl["dismissals"])
    bat_h2h_bowl.sort_values(by = 'balls_faced',inplace=True,ascending=False)
    bat_h2h_bowl = bat_h2h_bowl.round({'strike_rate':2,'balls_per_out':1})
    bat_h2h_style = bat_h2h_bowl.groupby(['bowling_style'])["balls_faced"].agg(balls_faced="sum").reset_index()
    bat_h2h_style["runs_total"] = bat_h2h_bowl.groupby(['bowling_style'])["runs_total"].agg(runs_total="sum").reset_index()["runs_total"]
    bat_h2h_style["dismissals"] = bat_h2h_bowl.groupby(['bowling_style'])["dismissals"].agg(dismissals="sum").reset_index()["dismissals"]
    bat_h2h_style.sort_values(by = 'balls_faced',inplace=True,ascending=False)
    bat_h2h_style["strike_rate"] = (bat_h2h_style["runs_total"]*100/bat_h2h_style["balls_faced"])
    bat_h2h_style["balls_per_out"] = (bat_h2h_style["balls_faced"]/bat_h2h_style["dismissals"])
    bat_h2h_style = bat_h2h_style.round({'strike_rate':2,'balls_per_out':1})

    return bat_h2h_bowl,bat_h2h_style



def player_charting(player = "MS Dhoni"):
    #importing relevant modules
    import pandas as pd
    import numpy as np
    import os

    cwd = os.getcwd()
    
    df = pd.read_csv(cwd+"/data/all_matches.csv",dtype = {'match_id':'int', 'season':'str','innings':'int', 'ball':'float'},parse_dates=True)
    df.season = df.season.replace({"2007/08": "2008","2009/10": "2010","2020/21":"2020"})

    players = pd.read_csv("player_details.csv")

    chart_df_pp_bowl , chart_df_pp_style = h2h_filter(over_filter(df = df,min_over=1,max_over=6),players,batsman=player)

    chart_df_mid_bowl , chart_df_mid_style = h2h_filter(over_filter(df = df,min_over=7,max_over=15),players,batsman=player)

    chart_df_death_bowl,chart_df_death_style = h2h_filter(over_filter(df = df,min_over=16,max_over=20),players,batsman=player)

    return chart_df_pp_bowl,chart_df_mid_bowl,chart_df_death_bowl,chart_df_pp_style,chart_df_mid_style,chart_df_death_style


