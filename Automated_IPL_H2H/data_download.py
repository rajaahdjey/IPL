#ref for downloading and importing from internet : https://stackoverflow.com/questions/6861323/download-and-unzip-file-with-python

import urllib.request
import zipfile
import os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

cwd = os.getcwd()
    
url = "https://cricsheet.org/downloads/ipl_csv2.zip"
extract_dir = cwd+"/data"

zip_path, _ = urllib.request.urlretrieve(url)
with zipfile.ZipFile(zip_path, "r") as f:
    f.extractall(extract_dir)


#now we start to process the data - import necessary libraries
import pandas as pd
import numpy as np

df = pd.read_csv(cwd+"/data/all_matches.csv",dtype = {'match_id':'int', 'season':'str','innings':'int', 'ball':'float'},parse_dates=True)
df.season = df.season.replace({"2007/08": "2008","2009/10": "2010","2020/21":"2020"})

#This block functions to get the list of unique players who have played in IPL - taken from team sheet

print("Getting list of unique players in IPL...")

import re
ipl_players = pd.DataFrame(columns=["season","team","player_name","identifier"])
for mat_id in df.match_id.unique():
    temp_df = pd.read_csv(f"{cwd}/data/{mat_id}_info.csv",sep='delimiter',engine='python')
    season = temp_df.iloc[4][-1].split(",")[-1]
    exploded_player_list = temp_df[temp_df.columns[0]].loc[20:41]
    people_registry = ",".join(temp_df[temp_df.columns[0]].loc[42:].values)
    for player in exploded_player_list:
        #print(player)
        try:
            df_row = []
            df_row.append(season)
            df_row.append(player.split(",")[2]) #team name
            df_row.append(player.split(",")[3]) #player name
            name = player.split(",")[3]
            df_row.append((re.findall(f"(?<={name},)(\w*)",people_registry))[0])
            #print(df_row)
            a_series = pd.Series(df_row, index = ipl_players.columns)
            ipl_players = ipl_players.append(a_series, ignore_index=True)
            #print("Try Succeeded")
        except:
            #print(f"Error for player {name}")
            pass

ipl_players.drop_duplicates(subset=["season","identifier"],inplace=True)

#now we import the people data from cricsheet - for cricinfo identifier

print("Importing data from cricsheet...")

people_url = "https://cricsheet.org/register/people.csv"
people_df = pd.read_csv(people_url,dtype = {"key_cricinfo":'str'})

merged_df = ipl_players.merge(people_df,how='left',on='identifier')
merged_df.drop(['key_cricbuzz','key_crichq', 'key_bigbash', 'key_cricinfo_2', 'key_cricingif', 'key_cricketarchive','key_cricketarchive_2', 'key_opta', 'key_opta_2', 'key_pulse','key_pulse_2'],axis = 1 , inplace=True)

#now we populate the player details for each of those players - fetching them from cricinfo website

print("Fetching player info from cricinfo...")

from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests

#ref : https://www.digitalocean.com/community/tutorials/how-to-work-with-web-data-using-requests-and-beautiful-soup-with-python-3

player_db = pd.DataFrame(columns=["key_cricinfo","player_name","batting_style","player_type","bowling_style"])
for player_id in merged_df.key_cricinfo.unique():
    #print("Player ID",player_id)
    url = f"https://www.espncricinfo.com/player/firstname-lastname-{player_id}"
    html = requests.get(url)
    soup = BeautifulSoup(html.text,'html.parser')
    res = soup.select(".ds-grid")
    player_d = []
    player_d.append(player_id)
    fields = []
    answers = []
    for r in res[0]:
        fields.append(r.find("p").text)
        answers.append(r.find("span").text)
    page_dict = dict(zip(fields, answers))
    player_d.append(page_dict["Full Name"])
    player_d.append(page_dict["Batting Style"])
    try:
        player_d.append(page_dict["Playing Role"])
        if(page_dict["Playing Role"]!="Wicketkeeper Batter"):
            player_d.append(page_dict["Bowling Style"])
        else:
            player_d.append("NA")
        a_series = pd.Series(player_d,index = player_db.columns)
        player_db = player_db.append(a_series, ignore_index=True)
    except:
        pass

#we merge the data and there will be a few not available info - which we had excepted

print("First merge into player list...")

final_player_df = pd.DataFrame()
final_player_df = merged_df.merge(player_db,how='left',on='key_cricinfo')
not_available = final_player_df[final_player_df['player_type'].isna()]

#a series of instructions to ensure we parse through those missing players and capture their data

print("Deep searching missing players...")

missing_db = pd.DataFrame(columns=["key_cricinfo","player_name","batting_style","player_type","bowling_style"])
for player_id in not_available.key_cricinfo.unique():
    #print("Player ID",player_id)
    url = f"https://www.espncricinfo.com/player/firstname-lastname-{player_id}"
    html = requests.get(url)
    soup = BeautifulSoup(html.text,'html.parser')
    res = soup.select(".ds-grid")
    player_d = []
    player_d.append(player_id)
    fields = []
    answers = []
    for r in res[0]:
        fields.append(r.find("p").text)
        answers.append(r.find("span").text)
    page_dict = dict(zip(fields, answers))
    player_d.append(page_dict["Full Name"])
    player_d.append(page_dict["Batting Style"])
    #if playing role is available and they are not bowlers 
    try:
        player_d.append(page_dict["Playing Role"])
        player_d.append("NA")
        a_series = pd.Series(player_d,index = missing_db.columns)
        missing_db = missing_db.append(a_series, ignore_index=True)
        # if playing role is not available ,we set it as NA in except
    except:
        player_d.append("NA")
        # check if player has bowling style
        try:
            player_d.append(page_dict["Bowling Style"])
            a_series = pd.Series(player_d,index = missing_db.columns)
            missing_db = missing_db.append(a_series, ignore_index=True)
        # if player doesn't have bowling style , then set that also as NA
        except:
            player_d.append("NA")
            a_series = pd.Series(player_d,index = missing_db.columns)
            missing_db = missing_db.append(a_series, ignore_index=True)
            pass
        pass

#set of final operations to clean up the df
print("Final cleaning of player dataframe...")

final_player_df = final_player_df.merge(missing_db,how='left',on='key_cricinfo')
final_player_df = final_player_df.fillna("")
final_player_df['batting_style_x'] = final_player_df['batting_style_x']+final_player_df['batting_style_y']
final_player_df.drop(["player_name_x","player_name_y"],axis=1,inplace=True)
final_player_df['player_type_x'] = final_player_df['player_type_x']+final_player_df['player_type_y']
final_player_df['bowling_style_x'] = final_player_df['bowling_style_x']+final_player_df['bowling_style_y']
final_player_df.drop("player_name",axis=1,inplace=True)
final_player_df.drop(['player_type_y','batting_style_y','bowling_style_y'],axis=1,inplace=True)
final_player_df.rename({'batting_style_x':'batting_style','player_type_x':'player_type','bowling_style_x':'bowling_style'},axis=1,inplace=True)

#finally we save the df to a csv


final_player_df.to_csv("player_details.csv")

print("player details saved!")