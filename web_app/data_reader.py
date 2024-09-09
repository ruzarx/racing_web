
import os
from datetime import date
from typing import Tuple, Dict, Optional
from dataclasses import dataclass, field

import pandas as pd

from utils.owners_to_teams import owners_to_teams

data_folder = '../data'
race_info_file_name = 'race_info.csv'
race_results_file_name = 'race_results.csv'
stage_results_file_name = 'top_10s.csv'

@dataclass(init=False)
class RaceResults:
    driver: str
    car_number: int
    manufacturer: str
    team: str
    start_position: int
    finish_position: int
    laps: int
    laps_led: int
    status: str
    points: int
    playoff_points: int
    stage_1_pos: Optional[int] = None
    stage_2_pos: Optional[int] = None
    stage_1_points: int = 0
    stage_2_points: int = 0

@dataclass(init=False)
class RaceData:
    race_date: date
    track: str



class DataReader:
    def __init__(self, season: int, race_name: str):
        self.season = season
        self.race_name = race_name
        self.race_folder = f"{data_folder}/{season}/{race_name}"

    def read_data(self):
        race_date, track = self._read_race_info()
        race_results = self._read_race_results()
        race_results = self._read_stage_results(race_results)
        for race in race_results:
            print(race_results[race])


    def _read_race_info(self) -> Tuple[date, str]:
        df = self._read_csv(race_info_file_name)
        race_date = pd.to_datetime(df['Date']).to_list()[0].date()
        track = df['Location'].to_list()[0].split(',')[0]
        return race_date, track
    
    def _read_race_results(self) -> Dict[int, RaceResults]:
        df = self._read_csv(race_results_file_name)
        race_results = {}
        for row in df.iterrows():
            driver_info = RaceResults()
            driver_info.driver = row[1]['Driver']
            driver_info.car_number = row[1]['#']
            driver_info.manufacturer = row[1]['Car']
            driver_info.team = self._get_team_name(row[1]['Sponsor / Owner'])
            driver_info.start_position = row[1]['St']
            driver_info.finish_position = row[1]['Pos']
            driver_info.laps = row[1]['Laps']
            driver_info.laps_led = row[1]['Led']
            driver_info.status = self._get_status(row[1]['Status'])
            driver_info.points = row[1]['Pts']
            driver_info.playoff_points = row[1]['PPts']
            race_results[row[1]['#']] = driver_info
        return race_results
    
    def _read_stage_results(self, race_results: Dict[int, RaceResults]):
        df = self._read_csv(stage_results_file_name)
        stage_points = 10
        for i, row in enumerate(df.iterrows()):
            stage_1_driver = int(row[1]["Top 10 in Stage 1:"].strip('#'))
            stage_2_driver = int(row[1]["Top 10 in Stage 2:"].strip('#'))
            race_results[stage_1_driver].stage_1_pos = i + 1
            race_results[stage_2_driver].stage_2_pos = i + 1
            race_results[stage_1_driver].stage_1_points = stage_points
            race_results[stage_2_driver].stage_2_points = stage_points
            stage_points -= 1
        return race_results

    
    def _read_csv(self, file_name: str) -> pd.DataFrame:
        df = pd.read_csv(f"{self.race_folder}/{file_name}")
        return df
    
    def _get_team_name(self, sponsor_owner: str) -> str:
        owner = sponsor_owner.split('(')[1][:-1]
        team_name = owners_to_teams.get(owner, 'Unknown Team')
        return team_name
    
    def _get_status(self, raw_status: str) -> str:
        if raw_status == 'running':
            status = 'finished'
        elif raw_status == 'crash':
            status = 'accident'
        else:
            status = 'mechanincal failure'
        return status
    
if __name__ == "__main__":
    DataReader(2024, 'USA Today 301').read_data()