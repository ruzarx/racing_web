from dataclasses import dataclass
from datetime import date

@dataclass(init=False)
class NascarRaceDataObject:
    season_year: int
    race_name: str
    race_number: int
    track_name: str
    race_date: date
    cautions_number: int
    green_flag_percent: float
    average_green_flag_run_laps: float
    number_of_leaders: int
    average_leading_run_laps: float
    most_laps_led: int
    most_laps_led_driver: str
    most_laps_led_percent: float


@dataclass(init=False)
class NascarRaceResultsObject:
    season_year: int
    race_number: int
    driver_name: str
    car_number: int
    team_name: str
    manufacturer: str
    race_pos: int
    quali_pos: int
    stage_1_pos: int
    stage_2_pos: int
    stage_3_pos: int
    laps_led: int
    status: str
    season_points: int
    finish_position_points: int
    stage_points: int
    playoff_points: int


@dataclass(init=False)
class NascarStandingsObject:
    season_year: int
    race_number: int
    driver_name: str
    race_season_points: int
    wins: int
    stage_wins: int
    race_playoff_points: int
    race_finish_points: int
    race_stage_points: int


@dataclass(init=False)
class NascarCalendarObject:
    season_year: int
    race_number: int
    track_name: str
    race_date: date
    season_stage: str
    