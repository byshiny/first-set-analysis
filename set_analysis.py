
# data is from https://github.com/JeffSackmann/tennis_atp

# TODO: 

# checkbox selector to graph the data and select the files you want
# first set win percentage by player

# deploy the app
# write the blog post





#total first set win percentage by player

#set the source 
# checkbox1 = st.checkbox("Checkbox 1")
# checkbox2 = st.checkbox("Checkbox 2")
# checkbox3 = st.checkbox("Checkbox 3")

# deploy the code


import streamlit as st
import pandas as pd
import numpy as np

st.title('Tennis ATP Data')
data_dir = './tennis_atp/atp_matches_2020.csv'
match_data = pd.read_csv(data_dir)

#print the first 10 rows of the data

sep_scores= match_data['score'].str.split(' ', expand=True)
print(sep_scores.columns)
first_set = sep_scores[0].str.split("-", expand = True)
first_set_series = (first_set[0] > first_set[1]).copy()
first_set_df =  pd.DataFrame(first_set_series, columns=["First Set Won"])
#create a new data framme with winner_name, loser_name and split scores

#scores = pd.concat([match_data["winner_name", "loser_name"]], ignore_index=True, sort=False)
#st.write(match_data["winner_name", "loser_name", "score"])

cur_scores = pd.concat([match_data[["winner_name", "loser_name", "best_of"]], first_set_df, sep_scores], axis=1)

filtered = cur_scores.loc[ cur_scores["winner_name"] == "Novak Djokovic" ]

first_set_won_count = sum(filtered["First Set Won"])
tot_matches = len(filtered)
print(first_set_won_count / tot_matches)
st.write(filtered)

# Create checkboxes
option1 = st.checkbox('Option 1')
option2 = st.checkbox('Option 2')
option3 = st.checkbox('Option 3')

# Create a button to trigger the action
if st.button('Print Selected Options'):
    selected_options = []
    if option1:
        selected_options.append('Option 1')
    if option2:
        selected_options.append('Option 2')
    if option3:
        selected_options.append('Option 3')
    
    if selected_options:
        st.write("Selected Options:")
        for option in selected_options:
            st.write(option)
    else:
        st.write("No options selected.")
