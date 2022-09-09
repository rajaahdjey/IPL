#import necessary libraries

import pandas as pd
import numpy as np
import os

cwd = os.getcwd()

df = pd.read_csv(cwd+"/data/all_matches.csv",dtype = {'match_id':'int', 'season':'str','innings':'int', 'ball':'float'},parse_dates=True)
df.season = df.season.replace({"2007/08": "2008","2009/10": "2010","2020/21":"2020"})

players = pd.read_csv("player_details.csv")

consolidated_df = pd.DataFrame()

consolidated_df = df.groupby(["striker"])["runs_off_bat"].agg(balls_faced="count",runs_total="sum").reset_index()

def over_filter(df = df,min_over=1,max_over=20):
    '''
    first over is counted from 0.1 to 0.6
    twentieth over is counted from 19.1 to 19.6
    '''
    temp_df = df[(df['ball']>(min_over-1)) & (df['ball']<=max_over)].groupby(["striker"])["runs_off_bat"].agg(balls_faced="count",runs_scored="sum").reset_index()
    temp_df["sr"] = temp_df["runs_scored"]*100/temp_df["balls_faced"]
    temp_df.rename(columns = {"sr":f"sr_{min_over}to{max_over}","balls_faced":f"balls_faced_{min_over}to{max_over}","runs_scored":f"runs_scored_{min_over}to{max_over}"},inplace=True)
    return temp_df


cons_df_pp = over_filter(df,1,6)
cons_df_mid = over_filter(df,7,15)
cons_df_death = over_filter(df,16,20)

consolidated_df = consolidated_df.merge(cons_df_pp,on='striker',how='left')
consolidated_df = consolidated_df.merge(cons_df_mid,on='striker',how='left')
consolidated_df = consolidated_df.merge(cons_df_death,on='striker',how='left')

consolidated_df.fillna(0,inplace=True)

consolidated_df["bat_salience_0to6"] = consolidated_df["balls_faced_0to6"]*100/consolidated_df["balls_faced"]
consolidated_df["bat_salience_7to15"] = consolidated_df["balls_faced_7to15"]*100/consolidated_df["balls_faced"]
consolidated_df["bat_salience_16to20"] = consolidated_df["balls_faced_16to20"]*100/consolidated_df["balls_faced"]

#ref to create and store named df from a list : https://stackoverflow.com/questions/67576606/create-multiple-empty-dataframes-named-from-a-list-using-a-loop

batsman_h2h_dict_7to15 = {}
batsman_style_dict_7to15 = {}
for batsman in consolidated_df["striker"]:
#for batsman in ["SK Raina"]: #for debugging
    df_7to15 = df[(df['ball']>6) & (df['ball']<=15)]
    df_batsman = df_7to15[df_7to15['striker'] == batsman]
    #print(df_batsman.shape)
    bat_h2h = df_batsman.groupby(['bowler'])["runs_off_bat"].agg(balls_faced="count",runs_total="sum").reset_index()
    bat_h2h["dismissals"] = df_batsman.groupby(['bowler'])["player_dismissed"].agg(balls_faced="count",dismissals="count").reset_index()["dismissals"]
    bat_h2h.sort_values(by = 'balls_faced',inplace=True,ascending=False)
    bat_h2h.rename({'bowler':'unique_name'},axis=1,inplace=True)
    bat_h2h_bowl = bat_h2h.merge(players,how='left',on='unique_name').drop(columns=['team','identifier','key_cricinfo','batting_style','name','player_type','season','Unnamed: 0'])
    bat_h2h_bowl.drop_duplicates(inplace=True)
    bat_h2h_bowl["strike_rate"] = (bat_h2h_bowl["runs_total"]*100/bat_h2h_bowl["balls_faced"])
    bat_h2h_bowl["balls_per_out"] = (bat_h2h_bowl["balls_faced"]/bat_h2h_bowl["dismissals"])
    bat_h2h_bowl = bat_h2h_bowl.round({'strike_rate':2,'balls_per_out':1})
    bat_h2h_style = bat_h2h_bowl.groupby(['bowling_style'])["balls_faced"].agg(balls_faced="sum").reset_index()
    bat_h2h_style["runs_total"] = bat_h2h_bowl.groupby(['bowling_style'])["runs_total"].agg(runs_total="sum").reset_index()["runs_total"]
    bat_h2h_style["dismissals"] = bat_h2h_bowl.groupby(['bowling_style'])["dismissals"].agg(dismissals="sum").reset_index()["dismissals"]
    bat_h2h_style.sort_values(by = 'balls_faced',inplace=True,ascending=False)
    bat_h2h_style["strike_rate"] = (bat_h2h_style["runs_total"]*100/bat_h2h_style["balls_faced"])
    bat_h2h_style["balls_per_out"] = (bat_h2h_style["balls_faced"]/bat_h2h_style["dismissals"])
    bat_h2h_style = bat_h2h_style.round({'strike_rate':2,'balls_per_out':1})
    
    batsman_h2h_dict_7to15[batsman] = bat_h2h_bowl
    batsman_style_dict_7to15[batsman] = bat_h2h_style
    