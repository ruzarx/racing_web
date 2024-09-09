from scrapper.db_scrapper import scrap_race
from scrapper.db_connectors import DBWriter
from scrapper.file_parsers import NascarRaceDataParser, NascarResultsParser

from flask import Flask

app = Flask(__name__)

writer = DBWriter(app, 'localhost/racing_data')

# writer.fill_tracks_info()

available_races = writer.get_available_races()

# writer.fill_calendar_info()

season = 2024
for race_number in range(1, 40):
    if (season, race_number) not in available_races:
        print(season, race_number)
        # is_success = scrap_race(season, race_number)
        # if not is_success:
        #     break
        race_data = NascarRaceDataParser(season, race_number).fill_race_data()
        writer.fill_race_data(race_data)
        # race_results, standings = NascarResultsParser(season, race_number).fill_results_data()
        # writer.fill_race_results(race_results)
        # writer.fill_standings(standings)
