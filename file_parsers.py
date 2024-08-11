from datetime import datetime
import pandas as pd
import numpy as np

from nascar_dataclasses import NascarRaceDataObject, NascarStandingsObject, NascarRaceResultsObject
from webpage.utils.owners_to_teams import owners_to_teams


class NascarRaceDataParser:
    def __init__(self, season: int, race_number: int):
        self.season = season
        self.race_number = race_number
        return

    def fill_race_data(self) -> NascarRaceDataObject:
        race_data_row = NascarRaceDataObject()
        race_data_row.season_year = self.season
        race_data_row.race_number = self.race_number

        race_name, track_name, race_date = self._load_track_data()
        race_data_row.race_name = race_name
        race_data_row.track_name = track_name
        race_data_row.race_date = race_date

        cautions_number, green_flag_percent, average_green_flag_run_laps = self._load_caution_data()
        race_data_row.cautions_number = int(cautions_number)
        race_data_row.green_flag_percent = float(green_flag_percent)
        race_data_row.average_green_flag_run_laps = float(average_green_flag_run_laps)

        (number_of_leaders,
        average_leading_run_laps,
        most_laps_led,
        most_laps_led_driver,
        most_laps_led_percent) = self._load_leaders_data()
        race_data_row.number_of_leaders = int(number_of_leaders)
        race_data_row.average_leading_run_laps = float(average_leading_run_laps)
        race_data_row.most_laps_led = int(most_laps_led)
        race_data_row.most_laps_led_driver = most_laps_led_driver
        race_data_row.most_laps_led_percent = float(most_laps_led_percent)

        return race_data_row

    def _load_track_data(self):
        track_data = pd.read_csv(f'data/{self.season}/{self.race_number}/race_info.csv')
        race_name = track_data['Name of the race'].values[0][5:]
        track_name = track_data['Location'].values[0].split(',')[0]
        raw_race_date = track_data['Date'].values[0]
        race_date = datetime.strptime(raw_race_date, "%A, %B %d, %Y").date()
        return race_name, track_name, race_date
    
    def _load_caution_data(self):
        caution_data = pd.read_csv(f'data/{self.season}/{self.race_number}/caution_flags.csv')
        cautions_number = caution_data[caution_data['Condition'] == 'yellow_flag']['# Of Laps'].count()

        n_green_laps = caution_data[caution_data['Condition'] == 'green_flag']['# Of Laps'].sum()
        n_yellow_laps = caution_data[caution_data['Condition'] == 'yellow_flag']['# Of Laps'].sum()
        green_flag_percent = n_green_laps / (n_yellow_laps + n_green_laps)

        average_green_flag_run_laps = caution_data[caution_data['Condition'] == 'green_flag']['# Of Laps'].mean()
        return cautions_number, green_flag_percent, average_green_flag_run_laps

    def _load_leaders_data(self):
        leaders_data = pd.read_csv(f'data/{self.season}/{self.race_number}/lap_leaders.csv')
        number_of_leaders = leaders_data['Leader'].nunique()
        average_leading_run_laps = leaders_data['# Of Laps'].mean()
        leaders = leaders_data[['Leader', '# Of Laps']].groupby(
            'Leader', as_index=False
            ).sum().sort_values('# Of Laps', ascending=False)
        most_laps_led = leaders['# Of Laps'].values[0]
        most_laps_led_driver = leaders['Leader'].values[0]
        most_laps_led_percent = most_laps_led / leaders['# Of Laps'].sum()
        return number_of_leaders, average_leading_run_laps, most_laps_led, most_laps_led_driver, most_laps_led_percent


class NascarResultsParser:
    def __init__(self, season: int, race_number: int):
        self.season = season
        self.race_number = race_number
        return

    def fill_results_data(self):
        results_data = pd.read_csv(f'data/{self.season}/{self.race_number}/race_results.csv')
        stages_results = self._load_stage_data()
        results_data = results_data.merge(stages_results, on='#', how='outer').fillna(0).sort_values('Pos', ascending=True)
        
        driver_names = results_data['Driver'].values
        car_numbers = [int(number) for number in results_data['#'].values]
        team_names = [self._fix_team_names(team_name) for team_name in results_data['Sponsor / Owner'].values]
        manufacturers = results_data['Car'].values
        race_pos = [int(pos) for pos in results_data['Pos'].values]
        quali_pos = [int(pos) for pos in results_data['St'].values]
        stage_1_pos = [int(pos) for pos in results_data['stage_1_pos'].values]
        stage_2_pos = [int(pos) for pos in results_data['stage_2_pos'].values]
        laps_leds = [int(laps) for laps in results_data['Led'].values]
        statuses = results_data['Status'].values
        season_points = [int(pts) for pts in results_data['Pts'].values]
        playoff_points = [int(pts) for pts in results_data['PPts'].values]
        finish_position_points = [40] + list(range(35, 0, -1)) + [1] * (results_data.shape[0] - 36)
        stage_points = [int(pts) for pts in (results_data['Pts'].values - np.array(finish_position_points))]
        wins = [1 if pos == 1 else 0 for pos in race_pos]
        stage_wins = [2 if (pos_stage_1 == 1) and (pos_stage_2 == 1) \
                    else 1 if (pos_stage_1 == 1) or (pos_stage_2 == 1) \
                        else 0 for pos_stage_1, pos_stage_2 in zip(stage_1_pos, stage_2_pos)]
        race_results = []
        for i in range(results_data.shape[0]):
            race_results_row = NascarRaceResultsObject()
            race_results_row.season_year = self.season
            race_results_row.race_number = self.race_number
            race_results_row.driver_name = driver_names[i]
            race_results_row.car_number = car_numbers[i]
            race_results_row.team_name = team_names[i]
            race_results_row.manufacturer = manufacturers[i]
            race_results_row.race_pos = race_pos[i]
            race_results_row.quali_pos = quali_pos[i]
            race_results_row.stage_1_pos = stage_1_pos[i]
            race_results_row.stage_2_pos = stage_2_pos[i]
            race_results_row.laps_led = laps_leds[i]
            race_results_row.status = statuses[i]
            race_results_row.season_points = season_points[i]
            race_results_row.finish_position_points = finish_position_points[i]
            race_results_row.stage_points = stage_points[i]
            race_results_row.playoff_points = playoff_points[i]
            race_results.append(race_results_row)
            
        standings = []
        for i in range(results_data.shape[0]):
            race_standings_row = NascarStandingsObject()
            race_standings_row.season_year = self.season
            race_standings_row.race_number = self.race_number
            race_standings_row.driver_name = driver_names[i]
            race_standings_row.race_season_points = season_points[i]
            race_standings_row.wins = wins[i]
            race_standings_row.stage_wins = stage_wins[i]
            race_standings_row.race_playoff_points = playoff_points[i]
            race_standings_row.race_finish_points = finish_position_points[i]
            race_standings_row.race_stage_points = stage_points[i]
            standings.append(race_standings_row)
        return race_results, standings
    
    def _fix_team_names(self, team_names: str) -> str:
        return owners_to_teams[team_names.split('(')[-1].strip(')')]

    def _load_stage_data(self):
        stage_data = pd.read_csv(f'data/{self.season}/{self.race_number}/top_10s.csv')
        stage_1 = [int(number.strip('#')) for number in stage_data["Top 10 in Stage 1:"].values]
        stage_2 = [int(number.strip('#')) for number in stage_data["Top 10 in Stage 2:"].values]
        stage_1_df = pd.DataFrame({'#': stage_1, 'stage_1_pos': list(range(1, 11))})
        stage_2_df = pd.DataFrame({'#': stage_2, 'stage_2_pos': list(range(1, 11))})
        stages_results = stage_1_df.merge(stage_2_df, on='#', how='outer')
        return stages_results
    