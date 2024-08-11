import sys
sys.path.append('.')

from datetime import date, datetime
from pathlib import Path
from collections import defaultdict, OrderedDict

import pandas as pd

from utils.owners_to_teams import owners_to_teams
from utils.tracks_to_types import tracks_to_types, tracks_to_short
from nascar_dataclasses import NascarCalendarObject



def fix_team_names(team_names: list) -> list:
    return [owners_to_teams[sponsor.split('(')[-1].strip(')')] for sponsor in team_names]

def load_track_data(season: int, race_folder: str):
    
    race_name = track_data['Name of the race'].values[0][5:]
    track_name = track_data['Location'].values[0].split(',')[0]
    track_type = tracks_to_types[track_name] if track_name in tracks_to_types else "Unknown"
    short_track_name = tracks_to_short[track_name] if track_name in tracks_to_short else "Unknown"
    raw_race_date = track_data['Date'].values[0]
    race_date = datetime.strptime(raw_race_date, "%A, %B %d, %Y").date()
    return race_name, track_name, race_date, track_type, short_track_name

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

def add_stage_results(race_results: pd.DataFrame, season: int, race_folder: str, current_results: dict):
    stage_data = pd.read_csv(f'data/{season}/{race_folder}/top_10s.csv')
    stage_1_winners = [int(res.strip('#')) for res in stage_data['Top 10 in Stage 1:'].values]
    stage_2_winners = [int(res.strip('#')) for res in stage_data['Top 10 in Stage 2:'].values]
    current_results['Stage 1'] = append_stage_data(stage_1_winners, race_results)
    current_results['Stage 2'] = append_stage_data(stage_2_winners, race_results)
    return current_results

def load_race_results(season: int, race_folder: str):
    race_results = pd.read_csv(f'data/{season}/{race_folder}/race_results.csv')
    if race_results.shape[0] < 3:
        return {'Qualification': {}, 'Race': {}, 'Stage 1': {}, 'Stage 2': {}}
    race_results['St'] = race_results['St'].astype(int)
    race_results['#'] = race_results['#'].astype(int)
    race_results['Pos'] = race_results['Pos'].astype(int)
    current_results = {}
    current_results['Race'] = {
            drivers: {
            'position': positions,
            'car_number': car_numbers,
            'team': teams,
            'manufacturer': manufacturers} for (drivers, positions, car_numbers, teams, manufacturers) in zip(
                race_results.sort_values('Pos')['Driver'].to_list(),
                race_results.sort_values('Pos')['Pos'].to_list(),
                race_results.sort_values('Pos')['#'].to_list(),
                fix_team_names(race_results.sort_values('Pos')['Sponsor / Owner'].to_list()),
                race_results.sort_values('Pos')['Car'].to_list()
            )}
    
    current_results = add_stage_results(race_results, season, race_folder, current_results)
    
    current_results['Qualification'] = {
                drivers: {
                'position': positions,
                'car_number': car_numbers,
                'team': teams,
                'manufacturer': manufacturers} for (drivers, positions, car_numbers, teams, manufacturers) in zip(
                    race_results.sort_values('St')['Driver'].to_list(),
                    race_results.sort_values('St')['St'].to_list(),
                    race_results.sort_values('St')['#'].to_list(),
                    fix_team_names(race_results.sort_values('St')['Sponsor / Owner'].to_list()),
                    race_results.sort_values('St')['Car'].to_list()
                )}
    return current_results



def load_race(season_year: str, race_number: int):
    race_name, track_name, race_date, track_type, short_track_name = load_track_data(season, race_folder)
    current_results = load_race_results(season, race_folder)
    current_race_data = {
        "name": race_name,
        "track": track_name,
        "date": race_date,
        "track_type": track_type,
        "track_type_short": "".join([word[0] for word in track_type.split(' ')]),
        "short_track": short_track_name,
        "image": "daytona.png" if race_date < date.today() else "daytona_bw.png",
        "results": current_results
    }
    return current_race_data

    
    

def load_nascar_data(season_year: str, race_number: int):
    current_race_data = load_race(season_year, race_number)
    return current_race_data


def calculate_statistics(driver_data):
    # Calculate statistics (average finish, etc.)
    # ...
    pass


def sort_months(month_name):
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    return month_order[month_name]

def compose_calendar_data(db_reader, selected_season: int):
    calendar_data = db_reader.get_calendar(selected_season)
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

    results['Qualification'] = {
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

