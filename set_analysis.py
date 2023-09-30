
import streamlit as st
import pandas as pd
import numpy as np
import requests 
import re
from io import StringIO
import plotly.express as px
import os
# win is:
# I get this working today
# 
# data is from https://github.com/JeffSackmann/tennis_atp

# TODO: 

# checkbox selector to graph the data and select the files you want
# first set win percentage by player

# deploy the app
# write the blog post


#total first set win percentage by player

github_username = "byshiny"
github_repository = "first-set-analysis"
github_directory = "tennis_data"


# GitHub API URL
api_url = f"https://api.github.com/repos/{github_username}/{github_repository}/contents/{github_directory}"

# Function to fetch and display files
@st.cache_data
def get_contents_from_github_directory():
    response = requests.get(api_url)
    
    if response.status_code == 200:
        contents = response.json()
        return contents

    else:
        st.error(f"Failed to retrieve contents: {response.status_code}")
        return []

# files = [item['name'] for item in contents if item['type'] == 'file']
# return files

@st.cache_data
def get_contents_from_local():
    files = os.listdir("./tennis_data")
    #create item with filename and file_url
    items = []
    for content in files:
        item = {}
        item["name"] = content
        item["download_url"] = f"./tennis_data/{content}"
        item["type"] = "file"
        items.append(item)
    return items


@st.cache_data
def get_filename_url_map_from_contents(contents):
    file_map = {item['name']: item['download_url'] for item in contents if item['type'] == 'file'}
    return file_map

def get_only_singles_match_data(filenames):
    # Find filenames that match the pattern
    pattern = r"atp_matches_\d+\.csv"
    single_matches_data = [filename for filename in filenames if re.match(pattern, filename)]
    return single_matches_data

@st.cache_data
def get_dataframe_from_url(download_url):
    # Make a request to download the CSV file
    print(download_url)
    csv_response = requests.get(download_url)
    print(csv_response.status_code)
    if csv_response.status_code == 200:
        # Read the CSV content into a Pandas DataFrame
        csv_content = csv_response.text
        df = pd.read_csv(StringIO(csv_content))
        return df

def get_first_set_win_percentage(winner_name):
    #filter by winner name and loser name 

    
    filtered = cur_scores.loc[ (cur_scores["winner_name"] == winner_name) | (cur_scores["loser_name"] == winner_name) ]
    first_set_won_count = sum(filtered["First Set Won"])
    tot_matches = len(filtered)
    if tot_matches == 0:
        return 0;
    first_set_win_percentage = first_set_won_count / tot_matches
    return first_set_win_percentage


# find the player who won the first set
def get_first_set_winner(row):
    #get the first set score
    first_set_score = row["score"].split(" ")[0]
    #split the first set score
    first_set = first_set_score.split("-")
    #extract first digit from string

    #get the first set winner
    first_set_winner = row["winner_name"] if int(first_set[0][0]) > int(first_set[1][0]) else row["loser_name"]
    return first_set_winner

contents = get_contents_from_github_directory()
filename_to_url_map = get_filename_url_map_from_contents(contents)
file_options = list(filename_to_url_map.keys())
single_matches_data = get_only_singles_match_data(file_options)
# reverse the list so the most recent matches are at the top
single_matches_data.reverse()

# Create a multiselect
selected_options = st.multiselect("Select Singles Matches by year:", single_matches_data)
selected_urls = [filename_to_url_map[key] for key in selected_options]

#  csv_url = item['download_url']
# Display the selected options
st.write("You selected:", selected_options)

if len(selected_urls) > 0:
    st.write("Downloading files...")
    dfs = [get_dataframe_from_url(selected_url) for selected_url in selected_urls]
    match_data = pd.concat(dfs, ignore_index=True, sort=False)

    #print the number of rows 
    st.write(match_data.shape[0])

    st.title('Sample 10 rows of Tennis ATP Data')

    #print first 10 rows of the data
    st.write(match_data.head(10))


    sep_scores= match_data['score'].str.split(' ', expand=True)

    first_set = sep_scores[0].str.split("-", expand = True)
    first_set_series = (first_set[0] > first_set[1]).copy()
    first_set_df =  pd.DataFrame(first_set_series, columns=["First Set Won"])
    #create a new data framme with winner_name, loser_name and split scores

    #find all the unique winner names
    winner_names = match_data['winner_name'].unique()

    winner_name = st.title("Show Matches by Player")

    #choose a single winner name 
    winner_name = st.selectbox("Select a player", winner_names)
    st.write(winner_name)

    #multiselect best of 3 or 5
    best_of_player = st.multiselect("Select best of 3 or 5 for the player", [3, 5])

    #select df if name is in winner name or loser name
    sample_winner_match_data = match_data.loc[ (match_data["winner_name"] == winner_name) | \
    (match_data["loser_name"] == winner_name) &  (match_data["best_of"].isin(best_of_player)) ]

    #get the first set winner for each row 
    sample_winner_match_data["first_set_winner"] = sample_winner_match_data.apply(get_first_set_winner, axis=1)

    st.write(sample_winner_match_data[["winner_name", "loser_name", "best_of", "score", "first_set_winner"]])

    # show total number of rows selected
    st.write(sample_winner_match_data.shape[0])

    #-----------------first set win percentage by player-----------------#

    st.title("First Set Win Percentage by Player")

    cur_scores = pd.concat([match_data[["winner_name", "loser_name", "best_of"]], first_set_df, sep_scores], axis=1)

    #multiselect best of 3 or 5
    best_of = st.multiselect("Select best of 3 or 5", [3, 5])

    #filter by number of matches played with steamlit slider 

    # get all names that appear in winner name and loser name
    all_names = pd.concat([match_data['winner_name'], match_data['loser_name']])
    #get the number of times each name appears
    name_counts = all_names.value_counts()
    #get the minimum and maximum number of matches played
    min_num_matches = name_counts.min()
    max_num_matches = name_counts.max()

    #show 20 name counts 
    st.write(name_counts.head(20))

    #create a slider to select the minimum number of matches
    min_matches = st.slider("Minimum number of matches", min_num_matches, max_num_matches, 10)

    winner_names = name_counts.loc[ name_counts >= min_matches ].index.tolist()


    if len(winner_names) > 0 and len(best_of) > 0:
        #filter by best of and min matches
        cur_scores = cur_scores.loc[ (cur_scores["best_of"].isin(best_of)) ]

        #find winner names and number of rows for each winner name as a map 

        #select by winner_names





        # #show total number of rows selected
        # st.write(cur_scores.shape[0])


        # #get first set win percentage for each winner name
        # print(winner_names)

        first_set_win_percentages = [get_first_set_win_percentage(winner_name) for winner_name in winner_names]
        # print(first_set_win_percentages)
        total_wins = [len(cur_scores.loc[ cur_scores["winner_name"] == winner_name ]) for winner_name in winner_names]
        
        # # get name counts for each winner name - refactor this to match names
        total_matches = [name_counts.loc[winner_name] for winner_name in winner_names]
        
        # #create a dataframe with winner name,  first set win percentage, total wins, and total_matches    
        first_set_win_percentages_df = pd.DataFrame({"winner_name": winner_names, \
             "first_set_win_percentage": first_set_win_percentages, "total_wins": total_wins, "total_matches": total_matches })
        # print(len(total_wins))
        # print("delim")
        # print(len(total_matches))
        # #sort by first set win percentage

        first_set_win_percentages_df = first_set_win_percentages_df.sort_values(by="first_set_win_percentage", ascending=False)
        # print("herro")
        st.write(first_set_win_percentages_df)

        #put a slider for the number of winner_names to show on the graph
        num_winners_to_show = st.slider("Number of winners to show", 1, len(winner_names), 10)

        #filter first_set_win_percentages_df by num_winners_to_show
        first_set_win_percentages_df = first_set_win_percentages_df.iloc[:num_winners_to_show]

        # graph win percentage and winner name
        fig = px.bar(first_set_win_percentages_df, x="winner_name", y="first_set_win_percentage", title="First Set Win Percentage by Winner Name")
        #draw a line at 
        st.plotly_chart(fig)





