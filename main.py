from nba_api.stats.endpoints import boxscoretraditionalv3
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from nba_api.stats.static import teams
import json

def find_all_nba_teamids():
    # Find all NBA teams
    nba_teams = teams.get_teams()
    team_ids = []
    for t in nba_teams:
        team_ids.append(t['id'])
    return team_ids

def find_all_nba_gameids(season="2023"):

    team_ids = find_all_nba_teamids()
    gamefinder = leaguegamefinder.LeagueGameFinder(season_type_nullable='Regular Season')
    games = gamefinder.get_data_frames()[0]

    # Convert SEASON_ID to string and split to SEASON_TYPE and SEASON_YEAR
    games['SEASON_ID'] = games['SEASON_ID'].apply(lambda x:str(x))
    games['GAME_ID'] = games['GAME_ID'].apply(lambda x: int(x))
    games['SEASON_TYPE'] = games['SEASON_ID'].str[:1]
    games['SEASON_YEAR'] = games['SEASON_ID'].str[-4:]

    # Filter only regular season NBA games in 2023-2024 season
    games = games.query('TEAM_ID in @team_ids & SEASON_YEAR == @season & GAME_ID < 1000000000')
    # Add leading 00 to GAME_ID
    games['GAME_ID'] = games['GAME_ID'].apply(lambda x: '00' + str(x))
    game_ids = games['GAME_ID'].unique()

    return game_ids

def boxscore_at_HT(game_ids='game_id.csv'):
    final = pd.DataFrame(columns=['GAME_ID', 'home_team','away_team','hs_minutes','hs_FGM','hs_FGA', 'hs_3PM', 'hs_3PA', 'hs_FTM',
                                  'hs_FTA', 'hs_OREB', 'hs_DREB', 'hs_AST', 'hs_STL', 'hs_BLK', 'hs_TO', 'hs_FOUL',
                                  'ht_minutes', 'ht_FGM', 'ht_FGA', 'ht_3PM', 'ht_3PA', 'ht_FTM', 'ht_FTA', 
                                  'ht_OREB', 'ht_DREB', 'ht_AST', 'ht_STL', 'ht_BLK', 'ht_TO', 'ht_FOUL',
                                  'as_minutes', 'as_FGM', 'as_FGA', 'as_3PM', 'as_3PA', 'as_FTM', 'as_FTA',
                                  'as_OREB', 'as_DREB', 'as_AST', 'as_STL', 'as_BLK', 'as_TO', 'as_FOUL',
                                  'at_minutes', 'at_FGM', 'at_FGA', 'at_3PM', 'at_3PA', 'at_FTM', 'at_FTA',
                                  'at_OREB', 'at_DREB', 'at_AST', 'at_STL', 'at_BLK', 'at_TO', 'at_FOUL'])


    game_id_df = pd.read_csv(game_ids)
    ids = game_id_df['GAME_ID']
    for g in ids:
        games = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id='00'+str(g), end_range=14400, end_period=10,
                                                            range_type=2, start_period=1, start_range=0)

        data = json.loads(games.get_json())

        # Pull starter and bench stats (note that boxscoretraditionalv3 is not pulling bench stats correctly.
        # Use team stats minus starter stats to obtain bench stats
        home_team = data['boxScoreTraditional']['homeTeam']['teamTricode']
        away_team = data['boxScoreTraditional']['awayTeam']['teamTricode']
        home_starter_stat = data['boxScoreTraditional']['homeTeam']['starters']
        home_team_stat = data['boxScoreTraditional']['homeTeam']['statistics']
        away_starter_stat = data['boxScoreTraditional']['awayTeam']['starters']
        away_team_stat = data['boxScoreTraditional']['awayTeam']['statistics']

        game_data = [g, home_team, away_team, home_starter_stat['minutes'], home_starter_stat['fieldGoalsMade'],
                         home_starter_stat['fieldGoalsAttempted'], home_starter_stat['threePointersMade'],
                         home_starter_stat['threePointersAttempted'],home_starter_stat['freeThrowsMade'],
                         home_starter_stat['freeThrowsAttempted'], home_starter_stat['reboundsOffensive'],
                         home_starter_stat['reboundsDefensive'], home_starter_stat['assists'], home_starter_stat['steals'],
                         home_starter_stat['blocks'], home_starter_stat['turnovers'], home_starter_stat['foulsPersonal'], 
                         home_team_stat['minutes'], home_team_stat['fieldGoalsMade'],
                         home_team_stat['fieldGoalsAttempted'], home_team_stat['threePointersMade'],
                         home_team_stat['threePointersAttempted'],home_team_stat['freeThrowsMade'],
                         home_team_stat['freeThrowsAttempted'], home_team_stat['reboundsOffensive'],
                         home_team_stat['reboundsDefensive'], home_team_stat['assists'], home_team_stat['steals'],
                         home_team_stat['blocks'], home_team_stat['turnovers'], home_team_stat['foulsPersonal'],
                         away_starter_stat['minutes'], away_starter_stat['fieldGoalsMade'],
                         away_starter_stat['fieldGoalsAttempted'], away_starter_stat['threePointersMade'],
                         away_starter_stat['threePointersAttempted'],away_starter_stat['freeThrowsMade'],
                         away_starter_stat['freeThrowsAttempted'], away_starter_stat['reboundsOffensive'],
                         away_starter_stat['reboundsDefensive'], away_starter_stat['assists'], away_starter_stat['steals'],
                         away_starter_stat['blocks'], away_starter_stat['turnovers'], away_starter_stat['foulsPersonal'],
                         away_team_stat['minutes'], away_team_stat['fieldGoalsMade'],
                         away_team_stat['fieldGoalsAttempted'], away_team_stat['threePointersMade'],
                         away_team_stat['threePointersAttempted'],away_team_stat['freeThrowsMade'],
                         away_team_stat['freeThrowsAttempted'], away_team_stat['reboundsOffensive'],
                         away_team_stat['reboundsDefensive'], away_team_stat['assists'], away_team_stat['steals'],
                         away_team_stat['blocks'], away_team_stat['turnovers'], away_team_stat['foulsPersonal']]
        final.loc[len(final)] = game_data

    final.to_csv('NBA_2023_Halftime_Boxscore.csv')

    return final

