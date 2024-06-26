# NBA Final Score Prediction
## Goal & Motivation
 Use boxscore at halftime to predict the final score (Use 2023-24 regular season). The motivation of this project is that we can place bet at final score of each team, total score, or score differential during halftime with hopefully enough data. If any of the final result falls outside the prediction interval, then we can place a bet and benefit!
## Data Source
All data were pulled from [nba_api](https://github.com/swar/nba_api) (Credit to Swar Patel).
## Project Description
### Data Pull
*main.py* (python) is used to pull the data. 
1. *find_all_nba_teamids*: pulls team_id for all NBA teams since the api also include non-NBA games. Returns a list of team ids.
2. *fina_all_nba_gameids*: pulls all game_ids for games played by NBA teams (from *find_all_nba_teamids*) in 2023-2024 regular season (including in-season tournament). Returns a list of game ids.
3. *boxscore_at_HT*: pulls box score of each game at halftime and split them by starter and total. Stats pulled include home/away, minutes, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, AST, STL, BLK, TO, and FOUL. The boxscore is pulled and compiled in a dataframe then export to a csv named *NBA_2023_Halftime_Boxscore.csv*.
### Initial Data Cleaning
*NBA Data Cleaning.ipynb* (python) was used to clean the data, and the following was done to the exported csv (*NBA_2023_Halftime_Boxscore.csv*) prior to analysis. 
- Since each row contains the box score from only 1 team (i.e. each game consists of 2 rows), I merged to create a 'wider' dataframe that separates stats from home team and away team.
- Reformatted number of minutes played by started from mm:ss:ms to a float (ex. 76:53:00 to 76.8833).
- Calculate bench stats by subtrating total stats by starter stats.
- Calculate 2PM & 2PA (2-point shot made/attemped) since FGA/FGM included both 3- and 2-point shots. 
- Calculate score of each team at halftime.
  
Finally, the dataframe was exported as *NBA_2023_halftime_boxscore_data_for_analysis.csv* for analysis
### Data Analysis & Visualization
*NBA Analysis.rmd* (R) was used for data analysis, and it was knitted to *NBA-Analysis.html*. The steps and rationale of each step of analysis is included in the notebook. The data was then trained using the parameters selected in python and saved as a pickle file to be use for modeling. 

### Perform Prediction
*live_boxscore.py* (python) was developed to checks if any of the games are at halftime currently, and if so, perform the following tasks in order: pull boxscore, predict final scores, and send predictions via email. 

## Conclusion
We can use the model to place bet at halftime if the line set by sportsbook is outside the desired prediction level and profit from it. Since [nba_api](https://github.com/swar/nba_api) has much more data than just box score, advanced data can be used to built a more accurate model. Also, machine learning may be experimented to develop a model that is more accurate (but more complicated) than a regression model. 

Furthermore, we can use an API to access the live betting line and compare against prediction, and only send notification when the betting line is outside the prediction interval. 
