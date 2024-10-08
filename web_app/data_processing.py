import sys
sys.path.append('.')

from datetime import date, datetime
from pathlib import Path
from collections import defaultdict, OrderedDict

import pandas as pd

from utils.owners_to_teams import owners_to_teams
from utils.tracks_to_types import tracks_to_types, tracks_to_short

from standings_calculation import standings_calculation

def fix_team_names(team_names: list) -> list:
    return [owners_to_teams[sponsor.split('(')[-1].strip(')')] for sponsor in team_names]


def append_stage_data(stage_winners: list, race_results: pd.DataFrame):
    positions = []
    drivers = []
    car_numbers = []
    teams = []
    manufacturers = []
    for pos, winner_number in enumerate(stage_winners):
        positions.append(pos + 1)
        drivers.append(race_results[race_results['#'] == winner_number]['Driver'].values[0])
        car_numbers.append(winner_number)
        teams.append(race_results[race_results['#'] == winner_number]['Sponsor / Owner'].values[0])
        manufacturers.append(race_results[race_results['#'] == winner_number]['Car'].values[0])
    return {
        driver: {
        'position': position,
        'car_number': car_number,
        'team': team,
        'manufacturer': manufacturer} for (driver, position, car_number, team, manufacturer) in zip(
            drivers,
            positions,
            car_numbers,
            fix_team_names(teams),
            manufacturers
        )}

def sort_months(month_name):
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    return month_order[month_name]

def compose_calendar_data(calendar_data: dict):
    
    calendar_data_dict = defaultdict(list)
    for race_info in calendar_data:
        month_name = race_info["race_date"].strftime("%B")
        calendar_data_dict[month_name].append(race_info)

    for month_name in calendar_data_dict.keys():
        calendar_data_dict[month_name].sort(key=lambda race: race["race_date"])

    sorted_months = sorted(calendar_data_dict.keys(), key=sort_months)
    ordered_calendar_data = OrderedDict()
    for month in sorted_months:
        ordered_calendar_data[month] = calendar_data_dict[month]
    return ordered_calendar_data

def compose_race_results(raw_race_results) -> dict:
    race_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_race_results],
                              'car_number': [res['car_number'] for res in raw_race_results],
                              'team_name': [res['team_name'] for res in raw_race_results],
                              'manufacturer': [res['manufacturer'] for res in raw_race_results],
                              'race_pos': [res['race_pos'] for res in raw_race_results],
                              'quali_pos': [res['quali_pos'] for res in raw_race_results],
                              'laps_led': [res['laps_led'] for res in raw_race_results],
                              'status': [res['status'] for res in raw_race_results]})
    race_data = race_data.sort_values(by=['race_pos'], ascending=True)
    results = {}
    results['Race'] = {
        drivers: {
            'position': positions,
            'car_number': car_numbers,
            'team': teams,
            'make': makes,
            'laps_led': laps_leds,
            'status': statuses,
        } for (drivers, positions, car_numbers, teams, makes, laps_leds, statuses) in zip(
                race_data['driver_name'].tolist(),
                race_data['race_pos'].tolist(),
                race_data['car_number'].tolist(),
                race_data['team_name'].tolist(),
                race_data['manufacturer'].tolist(),
                race_data['laps_led'].tolist(),
                race_data['status'].tolist(),
        )}
        

    quali_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_race_results],
                            'car_number': [res['car_number'] for res in raw_race_results],
                            'team_name': [res['team_name'] for res in raw_race_results],
                            'manufacturer': [res['manufacturer'] for res in raw_race_results],
                            'start_position': [res['quali_pos'] for res in raw_race_results],})
    quali_data = quali_data.sort_values(by=['start_position'], ascending=True)

    results['Qualifying'] = {
        drivers: {
            'position': positions,
            'car_number': car_numbers,
            'team': teams,
            'make': makes,
        } for (drivers, positions, car_numbers, teams, makes) in zip(
                quali_data['driver_name'].tolist(),
                quali_data['start_position'].tolist(),
                quali_data['car_number'].tolist(),
                quali_data['team_name'].tolist(),
                quali_data['manufacturer'].tolist(),
        )}

    stage_1_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_race_results],
                            'car_number': [res['car_number'] for res in raw_race_results],
                            'team_name': [res['team_name'] for res in raw_race_results],
                            'manufacturer': [res['manufacturer'] for res in raw_race_results],
                            'stage_1_pos': [res['stage_1_pos'] for res in raw_race_results],})
    stage_1_data = stage_1_data[stage_1_data['stage_1_pos'] > 0].sort_values(by=['stage_1_pos'], ascending=True)
    results['Stage 1'] = {
        drivers: {
            'position': positions,
            'car_number': car_numbers,
            'team': teams,
            'make': makes,
        } for (drivers, positions, car_numbers, teams, makes) in zip(
                stage_1_data['driver_name'].tolist(),
                stage_1_data['stage_1_pos'].tolist(),
                stage_1_data['car_number'].tolist(),
                stage_1_data['team_name'].tolist(),
                stage_1_data['manufacturer'].tolist(),
        )}

    stage_2_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_race_results],
                            'car_number': [res['car_number'] for res in raw_race_results],
                            'team_name': [res['team_name'] for res in raw_race_results],
                            'manufacturer': [res['manufacturer'] for res in raw_race_results],
                            'stage_2_pos': [res['stage_2_pos'] for res in raw_race_results],})
    stage_2_data = stage_2_data[stage_2_data['stage_2_pos'] > 0].sort_values(by=['stage_2_pos'], ascending=True)
    results['Stage 2'] = {
        drivers: {
            'position': positions,
            'car_number': car_numbers,
            'team': teams,
            'make': makes,
        } for (drivers, positions, car_numbers, teams, makes) in zip(
                stage_2_data['driver_name'].tolist(),
                stage_2_data['stage_2_pos'].tolist(),
                stage_2_data['car_number'].tolist(),
                stage_2_data['team_name'].tolist(),
                stage_2_data['manufacturer'].tolist(),
        )}
    return results

def compose_race_details(raw_results: dict) -> dict:
    race_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_results],
                              'race_pos': [res['race_pos'] for res in raw_results],
                              'laps_led': [res['laps_led'] for res in raw_results],
                              'status': [res['status'] for res in raw_results],
                              'season_points': [res['season_points'] for res in raw_results],
                              'finish_position_points': [res['finish_position_points'] for res in raw_results],
                              'stage_points': [res['stage_points'] for res in raw_results],
                              'playoff_points': [res['playoff_points'] for res in raw_results]})
    race_data = race_data.sort_values(by=['race_pos'], ascending=True)

    results = {}
    results['Race Details'] = {
        drivers: {
            'position': positions,
            'laps_led': laps_leds,
            'status': statuses,
            'season_points': season_pointses,
            'finish_position_points': finish_position_pointses,
            'stage_points': stage_pointses,
            'playoff_points': playoff_pointses,
        } for (drivers,
               positions,
               laps_leds,
               statuses,
               season_pointses,
               finish_position_pointses,
               stage_pointses,
               playoff_pointses) in zip(
                        race_data['driver_name'].tolist(),
                        race_data['race_pos'].tolist(),
                        race_data['laps_led'].tolist(),
                        [status if status != 'running' else 'finished' for status in race_data['status'].tolist()],
                        race_data['season_points'].tolist(),
                        race_data['finish_position_points'].tolist(),
                        race_data['stage_points'].tolist(),
                        race_data['playoff_points'].tolist(),
        )}
    return results

def compose_season_standings_data(raw_data: dict, race_number: str, current_season: str) -> dict:
    raw_standings_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_data],
                                  'wins': [res['wins'] for res in raw_data],
                                  'stage_wins': [res['stage_wins'] for res in raw_data],
                                  'race_stage_points': [res['race_stage_points'] for res in raw_data],
                                  'race_finish_points': [res['race_finish_points'] for res in raw_data],
                                  'race_season_points': [res['race_season_points'] for res in raw_data],
                                  'initial_season_points': [res['race_season_points'] for res in raw_data],
                                  'race_number': [res['race_number'] for res in raw_data]})
    
    standings_data = standings_calculation(raw_standings_data, int(race_number), int(current_season))
    standings_data = standings_data.sort_values(by=['season_points'], ascending=False)
    standings_data['pos'] = [x for x in range(1, len(standings_data) + 1)]

    results = {}
    results['Season_standings'] = {
        drivers: {
            'position': pos,
            'wins': wins,
            'stage_wins': stage_wins,
            'race_stage_points': race_stage_points,
            'race_finish_points': race_finish_points,
            'race_season_points': race_season_points,
            } for (drivers,
               wins,
               stage_wins,
               race_stage_points,
               race_finish_points,
               race_season_points,
               pos) in zip(
                        standings_data['driver_name'].tolist(),
                        standings_data['wins'].tolist(),
                        standings_data['stage_wins'].tolist(),
                        standings_data['race_stage_points'].tolist(),
                        standings_data['race_finish_points'].tolist(),
                        standings_data['season_points'].tolist(),
                        standings_data['pos'].tolist(),
               )
    }
    return results

def compose_playoff_standings_data(raw_data: dict, current_round: str, current_season: str) -> dict:
    current_race = int(current_round)
    raw_standings_data = pd.DataFrame({'driver_name': [res['driver_name'] for res in raw_data],
                                  'wins': [res['wins'] for res in raw_data],
                                  'stage_wins': [res['stage_wins'] for res in raw_data],
                                  'race_stage_points': [res['race_stage_points'] for res in raw_data],
                                  'race_finish_points': [res['race_finish_points'] for res in raw_data],
                                  'race_season_points': [res['race_season_points'] for res in raw_data],
                                  'initial_season_points': [res['race_season_points'] for res in raw_data],
                                  'race_number': [res['race_number'] for res in raw_data]})
    
    data = standings_calculation(raw_standings_data, current_race, int(current_season))

    if current_race <= 26:
        standings_data = compose_bubble(data, 16, 'season_wins')
    elif current_race <= 29:
        standings_data = compose_bubble(data, 12, 'playoff_16_wins')
    elif current_race <= 32:
        standings_data = compose_bubble(data, 8, 'playoff_12_wins')
    elif current_race <= 35:
        standings_data = compose_bubble(data, 4, 'playoff_8_wins')
    elif current_race == 36:
        standings_data = data.sort_values(by=['champion', 'season_points'], ascending=False).reset_index(drop=True)
        standings_data['pos'] = [x for x in range(1, len(standings_data) + 1)]
        standings_data['point_gap_to_leader'] = standings_data['season_points'] - \
            standings_data[standings_data['season_points'] == standings_data['season_points'].max()]['season_points'].tolist()[0]
        standings_data['point_gap_to_leader'] = standings_data['point_gap_to_leader'].fillna(0).astype(int).astype(str)


    results = {}
    results['Playoff_standings'] = {
        drivers: {
            'position': pos,
            'wins': wins,
            'stage_wins': stage_wins,
            'race_season_points': race_season_points,
            'point_gap_to_leader': point_gap_to_leader,
            'point_gap_to_bubble': point_gap_to_bubble,
            'race_playoff_points': playoff_points,
            } for (drivers,
               wins,
               stage_wins,
               race_season_points,
               point_gap_to_leader,
               point_gap_to_bubble,
               playoff_points,
               pos) in zip(
                        standings_data['driver_name'].tolist(),
                        standings_data['wins'].tolist(),
                        standings_data['stage_wins'].tolist(),
                        standings_data['season_points'].tolist(),
                        standings_data['point_gap_to_leader'].tolist(),
                        standings_data['point_gap_to_bubble'].tolist(),
                        standings_data['playoff_points'].tolist(),
                        standings_data['pos'].tolist(),
               )
    }
    return results

def compose_bubble(data: pd.DataFrame, playoff_drivers: int, wins_column: str) -> pd.DataFrame:
    standings_data = data.sort_values(by=[wins_column, 'season_points'], ascending=False).reset_index(drop=True)
    standings_data['pos'] = [x for x in range(1, len(standings_data) + 1)]

    standings_data['point_gap_to_leader'] = standings_data['season_points'] - \
        standings_data[standings_data['season_points'] == standings_data['season_points'].max()]['season_points'].tolist()[0]

    standings_data['point_gap_to_leader'] = standings_data['point_gap_to_leader'].fillna(0).astype(int).astype(str)
    standings_data.loc[
        standings_data['season_points'] == standings_data['season_points'].max(),
        'point_gap_to_leader'] = 'Points Leader'

    standings_data.loc[
        standings_data['pos'] <= playoff_drivers,
        'point_gap_to_bubble'] = standings_data['season_points'] - \
            standings_data[standings_data['pos'] == playoff_drivers + 1]['season_points'].tolist()[0]
    standings_data.loc[
        standings_data['pos'] > playoff_drivers,
        'point_gap_to_bubble'] = standings_data['season_points'] - \
            standings_data[standings_data['pos'] == playoff_drivers]['season_points'].tolist()[0]
    standings_data['point_gap_to_bubble'] = standings_data['point_gap_to_bubble'].astype(int)
    standings_data.loc[
        standings_data['point_gap_to_bubble'] > 0,
        'point_gap_to_bubble'] = '+' + standings_data[standings_data['point_gap_to_bubble'] > 0].astype(str)
    standings_data.loc[standings_data[wins_column] > 0, 'point_gap_to_bubble'] = 'Locked In'
    return standings_data