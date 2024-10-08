from datetime import datetime
import sys
sys.path.append('..')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select

from utils.tracks_to_types import tracks_to_types, tracks_to_short

from scrapper.nascar_dataclasses import NascarRaceDataObject, NascarRaceResultsObject, NascarStandingsObject, NascarCalendarObject


class DBWriter:
    def __init__(self, app: Flask):
        self.app = app
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@postgres:5432/racing_db"
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/racing_data"
        self.db = SQLAlchemy(app)
        self.create_tables()  # Automatically create tables if they don't exist
        return

    def create_tables(self):
        """Creates all the necessary tables if they don't already exist."""
        with self.app.app_context():
            # Define models that need to be created (only once, not loaded dynamically)
            class NascarTrackData(self.db.Model):
                __tablename__ = 'nascar_track_data'
                track_name = self.db.Column(self.db.String(255), nullable=False, primary_key=True)
                track_short_name = self.db.Column(self.db.String(255), nullable=False)
                track_type = self.db.Column(self.db.String(255), nullable=False)
                track_type_short = self.db.Column(self.db.String(255), nullable=False)
                track_length_mi = self.db.Column(self.db.String(255), nullable=True)

            class NascarCalendar(self.db.Model):
                __tablename__ = 'nascar_calendar'
                season_year = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                race_number = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                track_name = self.db.Column(self.db.String(255), nullable=False)
                race_date = self.db.Column(self.db.Date, nullable=False)
                season_stage = self.db.Column(self.db.String(255), nullable=False)

            class NascarRaceData(self.db.Model):
                __tablename__ = 'nascar_race_data'
                season_year = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                race_number = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                race_name = self.db.Column(self.db.String(255), nullable=False)
                track_name = self.db.Column(self.db.String(255), nullable=False)
                race_date = self.db.Column(self.db.Date, nullable=False)
                cautions_number = self.db.Column(self.db.Integer, nullable=False)
                green_flag_percent = self.db.Column(self.db.Float, nullable=False)
                average_green_flag_run_laps = self.db.Column(self.db.Float, nullable=False)
                number_of_leaders = self.db.Column(self.db.Integer, nullable=False)
                average_leading_run_laps = self.db.Column(self.db.Float, nullable=False)
                most_laps_led = self.db.Column(self.db.Integer, nullable=False)
                most_laps_led_driver = self.db.Column(self.db.String(255), nullable=False)
                most_laps_led_percent = self.db.Column(self.db.Float, nullable=False)

            class NascarRaceResults(self.db.Model):
                __tablename__ = 'nascar_race_results'
                season_year = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                race_number = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                driver_name = self.db.Column(self.db.String(255), nullable=False, primary_key=True)
                car_number = self.db.Column(self.db.String(255), nullable=False)
                team_name = self.db.Column(self.db.String(255), nullable=False)
                manufacturer = self.db.Column(self.db.String(255), nullable=False)
                race_pos = self.db.Column(self.db.Integer, nullable=False)
                quali_pos = self.db.Column(self.db.Integer, nullable=False)
                stage_1_pos = self.db.Column(self.db.Integer, nullable=False)
                stage_2_pos = self.db.Column(self.db.Integer, nullable=False)
                stage_3_pos = self.db.Column(self.db.Integer, nullable=False)
                laps_led = self.db.Column(self.db.Integer, nullable=False)
                status = self.db.Column(self.db.String(255), nullable=False)
                season_points = self.db.Column(self.db.Integer, nullable=False)
                finish_position_points = self.db.Column(self.db.Integer, nullable=False)
                stage_points = self.db.Column(self.db.Integer, nullable=False)
                playoff_points = self.db.Column(self.db.Integer, nullable=False)

            class NascarStandings(self.db.Model):
                __tablename__ = 'nascar_standings'
                season_year = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                race_number = self.db.Column(self.db.Integer, nullable=False, primary_key=True)
                driver_name = self.db.Column(self.db.String(255), nullable=False, primary_key=True)
                race_season_points = self.db.Column(self.db.Integer, nullable=False)
                wins = self.db.Column(self.db.Integer, nullable=False)
                stage_wins = self.db.Column(self.db.Integer, nullable=False)
                race_playoff_points = self.db.Column(self.db.Integer, nullable=False)
                race_finish_points = self.db.Column(self.db.Integer, nullable=False)
                race_stage_points = self.db.Column(self.db.Integer, nullable=False)

            # Create all tables
            self.db.create_all()
    
    def get_available_races(self) -> set:
        with self.app.app_context():
            query = text('SELECT season_year, race_number FROM nascar_race_results GROUP BY season_year, race_number')
            available_races = set(self.db.session.execute(query).fetchall())
        return available_races 

    def fill_tracks_info(self) -> None:
        with self.app.app_context():
            class TrackDataTable(self.db.Model):
                __tablename__ = 'nascar_track_data'
                __table_args__ = {'autoload_with': self.db.engine}
        
            for track_name in tracks_to_types.keys():
                track_type = tracks_to_types[track_name]
                track_short_name = tracks_to_short[track_name]
                track_type_short = "".join([word[0] for word in track_type.split(' ')])
                row = TrackDataTable(
                    track_name=track_name,
                    track_short_name=track_short_name,
                    track_type=track_type,
                    track_type_short=track_type_short,
                )
                self._commit_row(row)
        return
    
    def fill_calendar_info(self) -> None:
        from nascar_calendars import calendar_2023, calendar_2024

        with self.app.app_context():
            class CalendarTable(self.db.Model):
                __tablename__ = 'nascar_calendar'
                __table_args__ = {'autoload_with': self.db.engine}
        
            seasons = {2023: calendar_2023, 2024: calendar_2024}
            for season, current_calendar in seasons.items():
                for race_number, race_info in enumerate(current_calendar):
                    track_name = race_info[0]
                    race_date = datetime.strptime(race_info[1], '%d-%m-%Y').date()
                    season_stage = race_info[2]
                    row = CalendarTable(
                        season_year=season,
                        race_number=race_number + 1,
                        track_name=track_name,
                        race_date=race_date,
                        season_stage=season_stage,
                    )
                    self._commit_row(row)
        return

    def fill_race_data(self, data: NascarRaceDataObject) -> None:
        with self.app.app_context():
            class RaceDataTable(self.db.Model):
                __tablename__ = 'nascar_race_data'
                __table_args__ = {'autoload_with': self.db.engine}

            new_data = RaceDataTable(
                season_year=data.season_year,
                race_name=data.race_name,
                race_number=data.race_number,
                track_name=data.track_name,
                race_date=data.race_date,
                cautions_number=data.cautions_number,
                green_flag_percent=data.green_flag_percent,
                average_green_flag_run_laps=data.average_green_flag_run_laps,
                number_of_leaders=data.number_of_leaders,
                average_leading_run_laps=data.average_leading_run_laps,
                most_laps_led=data.most_laps_led,
                most_laps_led_driver=data.most_laps_led_driver,
                most_laps_led_percent=data.most_laps_led_percent,
            )
            self._commit_row(new_data)
        return
    
    def fill_race_results(self, race_results: NascarRaceResultsObject) -> None:
        with self.app.app_context():
            class RaceResultsTable(self.db.Model):
                __tablename__ = 'nascar_race_results'
                __table_args__ = {'autoload_with': self.db.engine}  

            for data in race_results:
                new_data = RaceResultsTable(
                    season_year=data.season_year,
                    race_number=data.race_number,
                    driver_name=data.driver_name,
                    car_number=data.car_number,
                    team_name=data.team_name,
                    manufacturer=data.manufacturer,
                    race_pos=data.race_pos,
                    quali_pos=data.quali_pos,
                    stage_1_pos=data.stage_1_pos,
                    stage_2_pos=data.stage_2_pos,
                    stage_3_pos=data.stage_3_pos,
                    laps_led=data.laps_led,
                    status=data.status,
                    season_points=data.season_points,
                    finish_position_points=data.finish_position_points,
                    stage_points=data.stage_points,
                    playoff_points=data.playoff_points,
                )
                self._commit_row(new_data)
        return

    def fill_standings(self, race_standings: NascarStandingsObject) -> None:
        with self.app.app_context():
            class RaceStandingsTable(self.db.Model):
                __tablename__ = 'nascar_standings'
                __table_args__ = {'autoload_with': self.db.engine}

            for data in race_standings:
                new_data = RaceStandingsTable(
                    season_year=data.season_year,
                    race_number=data.race_number,
                    driver_name=data.driver_name,
                    race_season_points=data.race_season_points,
                    wins=data.wins,
                    stage_wins=data.stage_wins,
                    race_playoff_points=data.race_playoff_points,
                    race_finish_points=data.race_finish_points,
                    race_stage_points=data.race_stage_points,
                )
                self._commit_row(new_data)
        return

    def _commit_row(self, row) -> None:
        try:
            self.db.session.add(row)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
        return


class DBReader:
    def __init__(self, app: Flask):
        self.app = app
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/racing_db'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/racing_data'
        
        self.db = SQLAlchemy(app)
        return
    
    def get_race_data(self, season_year: str, race_number: str) -> NascarRaceDataObject:
        with self.app.app_context():
            class RaceDataTable(self.db.Model):
                __tablename__ = 'nascar_race_data'
                __table_args__ = {'autoload_with': self.db.engine}

            class TrackDataTable(self.db.Model):
                __tablename__ = 'nascar_track_data'
                __table_args__ = {'autoload_with': self.db.engine}
            
            query = (
                select(RaceDataTable, TrackDataTable)
                .select_from(RaceDataTable).filter_by(season_year=int(season_year), race_number=int(race_number))
                .join(TrackDataTable, onclause=(RaceDataTable.track_name == TrackDataTable.track_name))
            )
            race_data = self.db.session.execute(query).fetchall()

            if race_data:
                return {
                    "track_type": race_data[0][1].track_type,
                    "track_name": race_data[0][1].track_name,
                    "race_name": race_data[0][0].race_name,
                    "race_date": race_data[0][0].race_date,
                }
            
    def get_race_results(self, season: int, race_number: int) -> list:
        with self.app.app_context():
            class RaceResultsTable(self.db.Model):
                __tablename__ = 'nascar_race_results'
                __table_args__ = {'autoload_with': self.db.engine}

            race_results = self.db.session.query(RaceResultsTable).filter_by(season_year=season, race_number=race_number).all()
            if race_results:
                return [
                    {
                        "driver_name": result.driver_name,
                        "car_number": result.car_number,
                        "team_name": result.team_name,
                        "manufacturer": result.manufacturer,
                        "race_pos": result.race_pos,
                        "quali_pos": result.quali_pos,
                        "stage_1_pos": result.stage_1_pos,
                        "stage_2_pos": result.stage_2_pos,
                        "stage_3_pos": result.stage_3_pos,
                        "laps_led": result.laps_led,
                        "status": result.status,
                        "season_points": result.season_points,
                        "finish_position_points": result.finish_position_points,
                        "stage_points": result.stage_points,
                        "playoff_points": result.playoff_points,
                     } for result in race_results
                ]
            
    def get_season_standings_data(self, season: int, race_number: int) -> NascarRaceResultsObject:
        with self.app.app_context():
            class RaceStandingsTable(self.db.Model):
                __tablename__ = 'nascar_standings'
                __table_args__ = {'autoload_with': self.db.engine}

            race_results = self.db.session.query(RaceStandingsTable).filter(
                RaceStandingsTable.season_year == season, 
                RaceStandingsTable.race_number <= race_number
            ).all()
            if race_results:
                return [
                    {
                        "driver_name": result.driver_name,
                        "wins": result.wins,
                        "stage_wins": result.stage_wins,
                        "race_stage_points": result.race_stage_points,
                        "race_finish_points": result.race_finish_points,
                        "race_season_points": result.race_season_points,
                        "race_playoff_points": result.race_playoff_points,
                        "race_number": result.race_number,
                     } for result in race_results
                ]
            
    def get_standings(self, season: int) -> NascarStandingsObject:
        with self.app.app_context():
            class RaceStandingsTable(self.db.Model):
                __tablename__ = 'nascar_standings'
                __table_args__ = {'autoload_with': self.db.engine}

            race_standings = self.db.session.query(RaceStandingsTable).filter_by(season_year=season).all()
            if race_standings:
                return [
                    NascarStandingsObject(
                        season_year=result.season_year,
                        race_number=result.race_number,
                        driver_name=result.driver_name,
                        race_season_points=result.race_season_points,
                        wins=result.wins,
                        stage_wins=result.stage_wins,
                        race_playoff_points=result.race_playoff_points,
                        race_finish_points=result.race_finish_points,
                        race_stage_points=result.race_stage_points,
                        ) for result in race_standings
                ]

    def get_calendar(self, season: int) -> dict:
        with self.app.app_context():
            class CalendarTable(self.db.Model):
                __tablename__ = 'nascar_calendar'
                __table_args__ = {'autoload_with': self.db.engine}

            class TrackDataTable(self.db.Model):
                __tablename__ = 'nascar_track_data'
                __table_args__ = {'autoload_with': self.db.engine}

            query = (
                select(CalendarTable, TrackDataTable)
                .select_from(CalendarTable).filter_by(season_year=season)
                .join(TrackDataTable, onclause=(CalendarTable.track_name == TrackDataTable.track_name))
            )
            calendar = self.db.session.execute(query).fetchall()
            season_calendar = []
            for result in calendar:
                current_race = {"season_year": str(result[0].season_year),
                    "race_number": str(result[0].race_number),
                    "track_name": result[0].track_name,
                    "track_short_name": result[1].track_short_name,
                    "race_date": result[0].race_date,
                    "track_type_short": result[1].track_type_short,
                    "season_stage": result[0].season_stage,
                    }
                season_calendar.append(current_race)
        return season_calendar
