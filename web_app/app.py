import sys
sys.path.append('.')
sys.path.append('..')

from flask import Flask, render_template, request
import data_processing
from datetime import date
import inflect

from scrapper.db_connectors import DBReader

import warnings
warnings.filterwarnings('ignore')


app = Flask(__name__)
app.jinja_env.filters['ordinal_suffix'] = inflect.engine().ordinal

db_reader = DBReader(app)


@app.route('/')
def index():
    welcome_message = "Welcome to Racing Analytics!"
    return render_template('base.html', welcome_message=welcome_message)


def sort_months(month_name):
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    return month_order[month_name]

@app.route('/nascar')
def nascar():
    selected_season = request.args.get('season', str(date.today().year))
    selected_race_number = request.args.get('race')
    if not selected_race_number:
        selected_race_number = 1
    raw_race_data = db_reader.get_race_data(selected_season, selected_race_number)
    raw_results = db_reader.get_race_results(selected_season, selected_race_number)
    raw_calendar_data = db_reader.get_calendar(selected_season)
    calendar_data = data_processing.compose_calendar_data(raw_calendar_data)
    raw_standings_data = db_reader.get_season_standings_data(selected_season, selected_race_number)
    if raw_race_data is not None:
        for race in raw_calendar_data:
            if race['race_number'] == selected_race_number:
                raw_race_data['season_stage'] = race['season_stage']
                break
    if raw_results is not None:
        race_details = data_processing.compose_race_details(raw_results)
        results = data_processing.compose_race_results(raw_results)
        season_standings_data = data_processing.compose_season_standings_data(raw_standings_data,
                                                                              selected_race_number,
                                                                              selected_season)
        playoff_standings_data = data_processing.compose_playoff_standings_data(raw_standings_data,
                                                                                selected_race_number,
                                                                                selected_season)
        raw_race_data['results'] = results
        selected_race_data = raw_race_data
    else:
        selected_race_data = None
        selected_race_number = None
        race_details = None
        season_standings_data = None
        playoff_standings_data = None

    return render_template(
        'nascar.html',
        calendar_data=calendar_data,
        selected_season=selected_season,
        selected_race=selected_race_number,
        selected_race_data=selected_race_data,
        selected_race_details=race_details,
        season_standings=season_standings_data,
        playoff_standings=playoff_standings_data,
    )


@app.route('/formula1')
def formula1():
    return render_template('formula1.html')

@app.route('/wec')
def wec():
    return render_template('wec.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
