import os
from nba_api.stats.endpoints import boxscoretraditionalv3
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from nba_api.stats.static import teams
import json
from datetime import date
from main import *
import re
from scipy import stats
import math
import smtplib
from email.mime.text import MIMEText
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

csv_for_cleaning_name = str(date.today()) + '_nba_for_cleaning.csv'
csv_for_analysis_name = str(date.today()) + '_nba_for_analysis.csv'
result_csv_name = str(date.today()) + '_nba_prediction.csv'
def live_boxscore(game_ids, csv):
    final = pd.DataFrame(
        columns=['GAME_ID', 'home_team', 'away_team', 'hs_minutes', 'hs_FGM', 'hs_FGA', 'hs_3PM', 'hs_3PA', 'hs_FTM',
                 'hs_FTA', 'hs_OREB', 'hs_DREB', 'hs_AST', 'hs_STL', 'hs_BLK', 'hs_TO', 'hs_FOUL',
                 'ht_minutes', 'ht_FGM', 'ht_FGA', 'ht_3PM', 'ht_3PA', 'ht_FTM', 'ht_FTA',
                 'ht_OREB', 'ht_DREB', 'ht_AST', 'ht_STL', 'ht_BLK', 'ht_TO', 'ht_FOUL',
                 'as_minutes', 'as_FGM', 'as_FGA', 'as_3PM', 'as_3PA', 'as_FTM', 'as_FTA',
                 'as_OREB', 'as_DREB', 'as_AST', 'as_STL', 'as_BLK', 'as_TO', 'as_FOUL',
                 'at_minutes', 'at_FGM', 'at_FGA', 'at_3PM', 'at_3PA', 'at_FTM', 'at_FTA',
                 'at_OREB', 'at_DREB', 'at_AST', 'at_STL', 'at_BLK', 'at_TO', 'at_FOUL'])
    for id in game_ids:
        try:
            data = json.loads(boxscore.BoxScore(id).get_json())['game']
            game_data = create_boxscore_df(data, id, 'live')
            final.loc[len(final)] = game_data
        except:
            pass

    final.to_csv(csv, index=False)

    return final

def transform_data(input_csv, output_csv):
    '''
    See NBA Data Cleaning.ipynb for data cleaning steps
    :param csv: csv file pulled using live_boxscore
    :return: None
    '''
    boxscore = pd.read_csv(input_csv)
    # Calculate home team bench stats
    boxscore['hb_FGM'] = boxscore['ht_FGM'] - boxscore['hs_FGM']
    boxscore['hb_FGA'] = boxscore['ht_FGA'] - boxscore['hs_FGA']
    boxscore['hb_3PM'] = boxscore['ht_3PM'] - boxscore['hs_3PM']
    boxscore['hb_3PA'] = boxscore['ht_3PA'] - boxscore['hs_3PA']
    boxscore['hb_FTM'] = boxscore['ht_FTM'] - boxscore['hs_FTM']
    boxscore['hb_FTA'] = boxscore['ht_FTA'] - boxscore['hs_FTA']
    boxscore['hb_OREB'] = boxscore['ht_OREB'] - boxscore['hs_OREB']
    boxscore['hb_DREB'] = boxscore['ht_DREB'] - boxscore['hs_DREB']
    boxscore['hb_AST'] = boxscore['ht_AST'] - boxscore['hs_AST']
    boxscore['hb_STL'] = boxscore['ht_STL'] - boxscore['hs_STL']
    boxscore['hb_BLK'] = boxscore['ht_BLK'] - boxscore['hs_BLK']
    boxscore['hb_TO'] = boxscore['ht_TO'] - boxscore['hs_TO']
    boxscore['hb_FOUL'] = boxscore['ht_FOUL'] - boxscore['hs_FOUL']
    # Calculate away team bench stats
    boxscore['ab_FGM'] = boxscore['at_FGM'] - boxscore['as_FGM']
    boxscore['ab_FGA'] = boxscore['at_FGA'] - boxscore['as_FGA']
    boxscore['ab_3PM'] = boxscore['at_3PM'] - boxscore['as_3PM']
    boxscore['ab_3PA'] = boxscore['at_3PA'] - boxscore['as_3PA']
    boxscore['ab_FTM'] = boxscore['at_FTM'] - boxscore['as_FTM']
    boxscore['ab_FTA'] = boxscore['at_FTA'] - boxscore['as_FTA']
    boxscore['ab_OREB'] = boxscore['at_OREB'] - boxscore['as_OREB']
    boxscore['ab_DREB'] = boxscore['at_DREB'] - boxscore['as_DREB']
    boxscore['ab_AST'] = boxscore['at_AST'] - boxscore['as_AST']
    boxscore['ab_STL'] = boxscore['at_STL'] - boxscore['as_STL']
    boxscore['ab_BLK'] = boxscore['at_BLK'] - boxscore['as_BLK']
    boxscore['ab_TO'] = boxscore['at_TO'] - boxscore['as_TO']
    boxscore['ab_FOUL'] = boxscore['at_FOUL'] - boxscore['as_FOUL']
    # Drop team stats for both home and away
    boxscore.drop(list(boxscore.filter(regex='t_')), axis=1, inplace=True)
    # Create home_away column
    home_away = ['home']*boxscore.shape[0] + ['away']*boxscore.shape[0]
    # Create duplicate row since it only pulled 1 row per game
    boxscore = pd.concat([boxscore, boxscore], axis=0)
    # Add home_away column
    boxscore['home_away'] = home_away

    # Split combined_df to home_df and away_df
    home_df = boxscore[boxscore['home_away'] == 'home'].drop(
        list(boxscore.filter(regex='as_|ab_|TEAM_ABBREVIATION')), axis=1)
    away_df = boxscore[boxscore['home_away'] == 'away'].drop(
        list(boxscore.filter(regex='hs_|hb_|TEAM_ABBREVIATION')), axis=1)

    # Rename columns
    home_df = home_df.rename({'home_team': 'team', 'away_team': 'against'}, axis=1).rename(
        columns=lambda x: re.sub(r'h(s|b)_', r'\1_', x)).reset_index(drop=True)
    away_df = away_df.rename({'away_team': 'team', 'home_team': 'against'}, axis=1).rename(
        columns=lambda x: re.sub(r'a(s|b)_', r'\1_', x)).reset_index(drop=True)

    # Combine home_df and away_df
    final_df = pd.concat([home_df, away_df], ignore_index=True, axis=0)
    # Total score at halftime
    final_df['PTS_ht'] = final_df.apply(
        lambda x: (x['s_FGM'] + x['b_FGM'] - (x['s_3PM'] + x['b_3PM'])) * 2 + (x['s_3PM'] + x['b_3PM']) * 3 + (
                    x['s_FTM'] + x['b_FTM']) * 1, axis=1)
    # Create column for opponent point at halftime
    final_df['GAME_ID_agst'] = final_df.apply(lambda x: str(x['GAME_ID']) + x['against'], axis=1)
    final_df['GAME_ID_team'] = final_df.apply(lambda x: str(x['GAME_ID']) + x['team'], axis=1)
    # Create dataframe for opponent point at halftime only, use this to merge
    opp_pts = final_df[['GAME_ID_agst', 'PTS_ht']]
    # Merge final_df and opp_pts
    final_df = final_df.merge(opp_pts, left_on='GAME_ID_team', right_on='GAME_ID_agst')
    # Drop uncessary columns
    final_df.drop(columns=['GAME_ID_team', 'GAME_ID_agst_x', 'GAME_ID_agst_y'], inplace=True)
    # Rename columns
    final_df.rename(columns={'PTS_ht_y': 'PTS_ht_opp', 'PTS_ht_x': 'PTS_ht'}, inplace=True)
    # Rename and replace value in home column
    final_df.rename(columns={'home_away': 'home'}, inplace=True)
    final_df['home'] = final_df['home'].apply(lambda x: 1 if x=='home' else 0)

    final_df.to_csv(output_csv, index=False)
def predict_with_model(input_csv=csv_for_analysis_name, output_csv=result_csv_name):
    '''
    See NBA-Analysis.html for model. All values were copies from the model
    :param csv: csv file name for analysis, string
    :return: No return. Generates results and output to a csv file
    '''
    data = pd.read_csv(input_csv)
    # Convert b_FTM, b_OREB, b_STL to log(value)+1 for calculation
    for colname in ['b_FTM', 'b_OREB', 'b_STL']:
        data[colname] = data[colname].apply(lambda x: math.log(x+1))
    # Load model
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    pred_interval = model.get_prediction(data).summary_frame(alpha=0.2).map(lambda x: round(x, 1))
    data = pred_interval[['mean', 'obs_ci_lower', 'obs_ci_upper']]
    print(data)
    data.to_csv(output_csv, index=False)

def send_email():
    sender_email = os.environ['sender_email']
    sender_password = os.environ['sender_password']
    recipient_email = os.environ['recipient_email']
    subject = f"NBA Prediction"
    body = """\
    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(pd.read_csv(result_csv_name).to_html())
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())

# Uses 2023 Playoff Games to test this function
def get_gameids_today():
    gameids_today = []
    live_scoreboard = scoreboard.ScoreBoard()
    board = live_scoreboard.get_dict()
    for game in board['scoreboard']['games']:
        # Check for games at halftime
        if (game["period"] == 2 and game["gameClock"] == "PT00M00.00S") or (game['gameStatusText'].lower() == "half"):
            gameids_today.append(game['gameId'])
    # Check if there's any game at halftime
    if len(gameids_today) > 0:
        live_boxscore(gameids_today, csv=csv_for_cleaning_name)
        transform_data(input_csv=csv_for_cleaning_name, output_csv=csv_for_analysis_name)
        predict_with_model(csv_for_analysis_name, result_csv_name)
        send_email()

def fit_model(training_data='NBA_2023_halftime_boxscore_data_for_analysis.csv'):
    '''
    Fit linear regression model developed in 'NBA Analysis.Rmd' using python for prediction. Saves a pickle file of the model locally.
    :param training_data: file name of csv used to train regression model, string
    :return: None
    '''
    # Model = PTS_final ~ s_minutes + s_3PM + s_3PA + s_DREB + s_BLK + s_TO + log(b_FTM + 1) + log(b_OREB + 1) +
    #   b_DREB +  b_AST + log(b_STL + 1) + b_FOUL + PTS_ht + PTS_ht_opp + home
    df = pd.read_csv(training_data)
    # Create dummy variable for home_away
    df['home'] = df['home_away'].apply(lambda x: 1 if x == 'home' else 0)

    # Convert b_FTM, b_OREB, b_STL to log(value)+1 for calculation
    for colname in ['b_FTM', 'b_OREB', 'b_STL']:
        df[colname] = df[colname].apply(lambda x: math.log(x+1))
    # Train model
    reg = smf.ols(formula='PTS_final ~ s_minutes + s_3PM + s_3PA + s_DREB + s_BLK + s_TO + b_FTM + b_OREB + b_DREB +\
     b_AST + b_STL + b_FOUL + PTS_ht + PTS_ht_opp + home', data=df).fit()
    # Save model to model.pkl
    with open('model.pkl', 'wb') as f:
        pickle.dump(reg, f)

get_gameids_today()

