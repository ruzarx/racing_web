from datetime import date, datetime
from pathlib import Path

import pandas as pd

from utils.owners_to_teams import owners_to_teams
from utils.tracks_to_types import tracks_to_types, tracks_to_short


def fix_team_names(team_names: list) -> list:
    return [owners_to_teams[sponsor.split('(')[-1].strip(')')] for sponsor in team_names]

def load_track_data(season: int, race_folder: str):
    track_data = pd.read_csv(f'data/{season}/{race_folder}/race_info.csv')
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



def load_race(season: int, race_folder: str):
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

    
    

def load_nascar_data(season):
    # Load data from JSON (replace with your actual data loading logic)
    data_dir = Path(f"data/{season}")
    race_data = []
    for race_folder in data_dir.iterdir():
        current_race_data = load_race(season, race_folder.name)
        race_data.append(current_race_data)
    return race_data


def calculate_statistics(driver_data):
    # Calculate statistics (average finish, etc.)
    # ...
    pass
