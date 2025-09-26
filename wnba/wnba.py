import pandas as pd
from py_ball import league, scoreboard
import numpy as np
import datetime as dt
from plugins.base_plugin.base_plugin import BasePlugin
from utils.app_utils import resolve_path
from utils.image_utils import resize_image
import logging


logger = logging.getLogger(__name__)

class Wnba(BasePlugin):

    def getData(self, settings):
            
            date = np.datetime64('today', 'D')
            formatDate = dt.datetime.strptime(str(date), '%Y-%m-%d').strftime('%m/%d/%Y')
            league_id = 10
            headers = {'Connection': 'keep-alive',
                    'Host': 'stats.nba.com',
                    'Origin': 'http://stats.nba.com',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'stats.nba.com',
                    'x-nba-stats-origin': 'stats',
                    'x-nba-stats-token': 'true',
                    'Accept-Language': 'en-US,en;q=0.9',
                    "X-NewRelic-ID": "VQECWF5UChAHUlNTBwgBVw==",
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'}
            players = league.League(headers=headers, endpoint='commonallplayers', league_id=league_id, season='2025-26', season_id='22025', current_season='1')
            player_df = pd.DataFrame(players.data['CommonAllPlayers'])
            player_data = player_df.loc[:, ['PERSON_ID', 'DISPLAY_FIRST_LAST', 'TEAM_CITY']]
            schedule = league.League(headers=headers, endpoint='leaguegamelog', league_id=league_id, season='2025-26', season_type='Regular Season', direction='ASC', player_or_team='T')
            schedule_df = pd.DataFrame(schedule.data['LeagueGameLog'])
            schedule_date = schedule_df.loc[:, ['GAME_DATE']]
            schedule_df['GameDate'] = schedule_date.apply(lambda x: pd.to_datetime(schedule_date['GAME_DATE']))
            schedule_df.set_index('GameDate', inplace=True)
            schedule_df['dateDiff'] = (schedule_df.index - date)
            closest = schedule_df['dateDiff'].idxmax()
            games = scoreboard.ScoreBoard(headers=headers, endpoint='scoreboardv2', league_id=league_id, game_date=date, day_offset='0')
            nearestGame = scoreboard.ScoreBoard(headers=headers, endpoint='scoreboardv2', league_id=league_id, game_date=closest, day_offset='0')
            scores = pd.DataFrame(games.data['LineScore'])
            latestScores = pd.DataFrame(nearestGame.data['LineScore'])
            def showGame():
                if scores.empty == True:
                    return latestScores
                else:
                    return scores    
            teams = showGame().loc[:, ['GAME_ID', 'TEAM_CITY_NAME', 'TEAM_NAME', 'PTS']]
            duplicate = teams['GAME_ID'].duplicated()
            teams1 = teams[duplicate == False]
            teams2 = teams[duplicate == True]
            mergedTeams = pd.merge(teams1, teams2, on="GAME_ID", how="inner")
            winners = mergedTeams['PTS_x'] > mergedTeams['PTS_y']
            tie = mergedTeams['PTS_x'] == mergedTeams['PTS_y']
            tie.name = 'tied'
            winners.name = 'winnersX'
            merged = mergedTeams.join(winners)
            merged = merged.join(tie)
            isNull = merged['PTS_x'].isnull()
            isNull.name = 'null'
            merged = merged.join(isNull)
            tied = 'tie'
            noGame = 'not started'
            class1 = ''
            class2 = ''

            def determineClass1(row):
                if row['winningTeam'] == 'not started':
                    return 'lost'
                elif row['tied'] == True:
                    return 'won'
                elif row['winnersX'] == True:
                    return 'won'
                else:
                    return 'lost'
            def determineClass2(row):
                if row['winningTeam'] == 'not started':
                    return 'lost'
                elif row['tied'] == True:
                    return 'won'
                elif row['winnersX'] == True:
                    return 'lost'
                else:
                    return 'won'

            def processWinners(row):
                    if row['null'] == True:
                        return noGame
                    elif row['tied'] == True:
                        return tied
                    elif row['winnersX'] == True:
                        return row['TEAM_NAME_x']
                    else:
                        return row['TEAM_NAME_y']
                
            merged['winningTeam'] = merged.apply(processWinners, axis=1)
            merged['winningClass1'] = merged.apply(determineClass1, axis=1)
            merged['winningClass2'] = merged.apply(determineClass2, axis=1)

            '''def iterate():

                for index, row in merged.iterrows():
                    print(f'{row['TEAM_NAME_x']} vs. {row['TEAM_NAME_y']} and...')
                    if row['null'] == True:
                        print(f'The game has {noGame}!')
                    elif row['tied'] == True:      
                        print(f'It was a {tied}!')
                    else:
                        print(f'{row['winningTeam']} won!')'''
            
            team = 'team'
            team2 = 'team2'
            score = 'score'
            score2 = 'score2'
            won = 'won'
            won2 = 'won2'
            data = {
                "plugin_settings": settings

            }
            def iterate():

                for index, row in merged.iterrows():
                    data[team + str(index+1)] = row['TEAM_NAME_x']
                    data[team2 + str(index+1)] = row['TEAM_NAME_y']
                    data[score + str(index+1)] = row['PTS_x']
                    data[score2 + str(index+1)] = row['PTS_y']
                    data[won + str(index+1)] = row['winningClass1']
                    data[won2 + str(index+1)] = row['winningClass2']
                    '''if row['null'] == True:
                        print(f'The game has {noGame}!')
                    elif row['tied'] == True:      
                        print(f'It was a {tied}!')
                    else:
                        print(f'{row['winningTeam']} won!')'''
                    
            iterate()


            return data
    
    
    
    def generate_image(self, settings, device_config):

        date = np.datetime64('today', 'D')
        formatDate = dt.datetime.strptime(str(date), '%Y-%m-%d').strftime('%m/%d/%Y')
        league_id = 10
        headers = {'Connection': 'keep-alive',
                'Host': 'stats.nba.com',
                'Origin': 'http://stats.nba.com',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'stats.nba.com',
                'x-nba-stats-origin': 'stats',
                'x-nba-stats-token': 'true',
                'Accept-Language': 'en-US,en;q=0.9',
                "X-NewRelic-ID": "VQECWF5UChAHUlNTBwgBVw==",
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'}
        players = league.League(headers=headers, endpoint='commonallplayers', league_id=league_id, season='2025-26', season_id='22025', current_season='1')
        player_df = pd.DataFrame(players.data['CommonAllPlayers'])
        player_data = player_df.loc[:, ['PERSON_ID', 'DISPLAY_FIRST_LAST', 'TEAM_CITY']]
        schedule = league.League(headers=headers, endpoint='leaguegamelog', league_id=league_id, season='2025-26', season_type='Regular Season', direction='ASC', player_or_team='T')
        schedule_df = pd.DataFrame(schedule.data['LeagueGameLog'])
        schedule_date = schedule_df.loc[:, ['GAME_DATE']]
        schedule_df['GameDate'] = schedule_date.apply(lambda x: pd.to_datetime(schedule_date['GAME_DATE']))
        schedule_df.set_index('GameDate', inplace=True)
        schedule_df['dateDiff'] = (schedule_df.index - date)
        closest = schedule_df['dateDiff'].idxmax()

        latestGames = schedule_df.loc[closest]


        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        image_template_params = self.getData(settings)
        
        image = self.render_image(dimensions, "wnba.html", "wnba.css", image_template_params)
        if not image:
            raise RuntimeError("Failed to take screenshot, please check logs.")
        return image


    