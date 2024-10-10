import pandas as pd

from penalties import penalties

def standings_calculation(raw_data: pd.DataFrame, current_race: int, season: int):
    data = raw_data[raw_data['race_number'] <= current_race].reset_index(drop=True)
    all_drivers = raw_data['driver_name'].unique()
    season_points = {driver: 0 for driver in all_drivers}
    season_wins = {}
    playoff_16_wins = {}
    playoff_12_wins = {}
    playoff_8_wins = {}
    playoff_points = {driver: 0 for driver in all_drivers}
    playoff_16_drivers = []
    playoff_12_drivers = []
    playoff_8_drivers = []
    playoff_4_drivers = []
    champion = None
    for race in range(1, current_race + 1):
        race_data = data[data['race_number'] == race]
        
        if race < 27:
            # Regular season
            for driver in race_data['driver_name'].unique():
                season_points[driver] += race_data[race_data['driver_name'] == driver]['race_season_points'].values[0]
                playoff_points[driver] += 5 * race_data[race_data['driver_name'] == driver]['wins'].values[0] + \
                    race_data[race_data['driver_name'] == driver]['stage_wins'].values[0]
                if race_data[race_data['driver_name'] == driver]['wins'].values[0] == 1:
                    season_wins[driver] = season_wins.get(driver, 0) + 1
        if race == 27:
            playoff_16_drivers = [driver for driver, _ in sorted(season_wins.items(), key=lambda item: item[1], reverse=True)]
            top_points_drivers = [driver for driver, _ in sorted(season_points.items(), key=lambda item: item[1], reverse=True)]
            i = 0
            while len(playoff_16_drivers) < 16:
                if top_points_drivers[i] not in playoff_16_drivers:
                    playoff_16_drivers.append(top_points_drivers[i])
                i += 1
            season_standings_points = [15, 10, 8, 7, 6, 5, 4, 3, 2, 1]
            i = 0
            for driver in top_points_drivers[:10]:
                if driver in playoff_16_drivers:
                    playoff_points[driver] += season_standings_points[i]
                i += 1
            for driver in playoff_16_drivers:
                season_points[driver] = 2000
                season_points[driver] += playoff_points[driver]
        if race in (27, 28, 29):
            for driver in race_data['driver_name'].unique():
                season_points[driver] += race_data[race_data['driver_name'] == driver]['race_season_points'].values[0]
                playoff_points[driver] += 5 * race_data[race_data['driver_name'] == driver]['wins'].values[0] + \
                    race_data[race_data['driver_name'] == driver]['stage_wins'].values[0]
                if race_data[race_data['driver_name'] == driver]['wins'].values[0] == 1:
                    if driver in playoff_16_drivers:
                        playoff_16_wins[driver] = playoff_16_wins.get(driver, 0) + 1
                    else:
                        season_wins[driver] = season_wins.get(driver, 0) + 1
        if race == 30:
            playoff_12_drivers = [driver for driver, _ in sorted(playoff_16_wins.items(), key=lambda item: item[1], reverse=True)]
            top_points_drivers = [driver for driver, _ in sorted(season_points.items(), key=lambda item: item[1], reverse=True)]
            i = 0
            while len(playoff_12_drivers) < 12:
                if top_points_drivers[i] not in playoff_12_drivers:
                    playoff_12_drivers.append(top_points_drivers[i])
                i += 1
            for driver in playoff_12_drivers:
                season_points[driver] = 3000
                season_points[driver] += playoff_points[driver]
        if race in (30, 31, 32):
            for driver in race_data['driver_name'].unique():
                season_points[driver] += race_data[race_data['driver_name'] == driver]['race_season_points'].values[0]
                playoff_points[driver] += 5 * race_data[race_data['driver_name'] == driver]['wins'].values[0] + \
                    race_data[race_data['driver_name'] == driver]['stage_wins'].values[0]
                if race_data[race_data['driver_name'] == driver]['wins'].values[0] == 1:
                    if driver in playoff_12_drivers:
                        playoff_12_wins[driver] = playoff_12_wins.get(driver, 0) + 1
                    else:
                        season_wins[driver] = season_wins.get(driver, 0) + 1
        if race == 33:
            playoff_8_drivers = [driver for driver, _ in sorted(playoff_12_wins.items(), key=lambda item: item[1], reverse=True)]
            top_points_drivers = [driver for driver, _ in sorted(season_points.items(), key=lambda item: item[1], reverse=True)]
            i = 0
            while len(playoff_8_drivers) < 8:
                if top_points_drivers[i] not in playoff_8_drivers:
                    playoff_8_drivers.append(top_points_drivers[i])
                i += 1
            for driver in playoff_8_drivers:
                season_points[driver] = 4000
                season_points[driver] += playoff_points[driver]
            for driver in playoff_12_drivers:
                if driver not in playoff_8_drivers:
                    season_points[driver] -= 1000
        if race in (33, 34, 35):
            for driver in race_data['driver_name'].unique():
                season_points[driver] += race_data[race_data['driver_name'] == driver]['race_season_points'].values[0]
                playoff_points[driver] += 5 * race_data[race_data['driver_name'] == driver]['wins'].values[0] + \
                    race_data[race_data['driver_name'] == driver]['stage_wins'].values[0]
                if race_data[race_data['driver_name'] == driver]['wins'].values[0] == 1:
                    if driver in playoff_8_drivers:
                        playoff_8_wins[driver] = playoff_8_wins.get(driver, 0) + 1
                    else:
                        season_wins[driver] = season_wins.get(driver, 0) + 1
        if race == 36:
            playoff_4_drivers = [driver for driver, _ in sorted(playoff_8_wins.items(), key=lambda item: item[1], reverse=True)]
            top_points_drivers = [driver for driver, _ in sorted(season_points.items(), key=lambda item: item[1], reverse=True)]
            i = 0
            while len(playoff_4_drivers) < 4:
                if top_points_drivers[i] not in playoff_4_drivers:
                    playoff_4_drivers.append(top_points_drivers[i])
                i += 1
            for driver in playoff_4_drivers:
                season_points[driver] = 5000
            for driver in playoff_8_drivers:
                if driver not in playoff_4_drivers:
                    season_points[driver] -= 2000
            for driver in race_data['driver_name'].unique():
                if driver in playoff_4_drivers:
                    season_points[driver] += race_data[race_data['driver_name'] == driver]['race_finish_points'].values[0]
                else:
                    season_points[driver] += race_data[race_data['driver_name'] == driver]['race_season_points'].values[0]
            champion = [driver for driver, _ in sorted(season_points.items(), key=lambda item: item[1], reverse=True)][0]
            for driver in playoff_4_drivers:
                if driver != champion:
                    season_points[driver] -= 3000
        season_points, playoff_points, season_wins, playoff_16_wins, playoff_12_wins, playoff_8_wins = apply_penalties(season,
                                                                     race,
                                                                     season_points,
                                                                     playoff_points,
                                                                     season_wins,
                                                                     playoff_16_wins,
                                                                     playoff_12_wins,
                                                                     playoff_8_wins)
    data = raw_data[
        ['driver_name', 'stage_wins', 'race_stage_points', 'race_finish_points']
        ].groupby('driver_name', as_index=False).sum()
    standings = pd.DataFrame({'driver_name': all_drivers,
                    'season_points': [season_points[driver] for driver in all_drivers],
                    'wins': [season_wins.get(driver, 0) + \
                            playoff_16_wins.get(driver, 0) + \
                            playoff_12_wins.get(driver, 0) + \
                            playoff_8_wins.get(driver, 0) + \
                            (driver == champion) for driver in all_drivers],
                    'season_wins': [season_wins.get(driver, 0) for driver in all_drivers],
                    'playoff_16_wins': [playoff_16_wins.get(driver, 0) for driver in all_drivers],
                    'playoff_12_wins': [playoff_12_wins.get(driver, 0) for driver in all_drivers],
                    'playoff_8_wins': [playoff_8_wins.get(driver, 0) for driver in all_drivers],
                    'stage_wins': [data[data['driver_name'] == driver]['stage_wins'].values[0] \
                                    if driver in data['driver_name'].unique() else 0 for driver in all_drivers],
                    'race_stage_points': [data[data['driver_name'] == driver]['race_stage_points'].values[0] \
                                    if driver in data['driver_name'].unique() else 0 for driver in all_drivers],
                    'race_finish_points': [data[data['driver_name'] == driver]['race_finish_points'].values[0] \
                                    if driver in data['driver_name'].unique() else 0 for driver in all_drivers],
                    'playoff_points': [playoff_points[driver] for driver in all_drivers],
                    'qualified_to_16': [1 if driver in playoff_16_drivers else 0 for driver in all_drivers],
                    'qualified_to_12': [1 if driver in playoff_12_drivers else 0 for driver in all_drivers],
                    'qualified_to_8': [1 if driver in playoff_8_drivers else 0 for driver in all_drivers],
                    'qualified_to_final': [1 if driver in playoff_4_drivers else 0 for driver in all_drivers],
                    'champion': [1 if driver == champion else 0 for driver in all_drivers]})
    return standings

def apply_penalties(season: int,
                    current_race: int,
                    season_points: dict,
                    playoff_points: dict,
                    season_wins: dict,
                    playoff_16_wins: dict,
                    playoff_12_wins: dict,
                    playoff_8_wins: dict):
    for _, record in penalties.items():
        if (record['season'] == season) and (record['race'] == current_race):
            if record['type'] == 'season_points':
                season_points[record['driver_name']] -= record['amount']
            elif record['type'] == 'playoff_points':
                playoff_points[record['driver_name']] -= record['amount']
            elif record['type'] == 'race_win':
                if current_race <= 26:
                    season_wins[record['driver_name']] = season_wins.get(record['driver_name'], 0) - 1
                    season_wins = delete_loser(season_wins, record['driver_name'])
                elif current_race <= 29:
                    playoff_16_wins[record['driver_name']] = playoff_16_wins.get(record['driver_name'], 0) - 1
                    playoff_16_wins = delete_loser(playoff_16_wins, record['driver_name'])
                elif current_race <= 32:
                    playoff_12_wins[record['driver_name']] = playoff_12_wins.get(record['driver_name'], 0) - 1
                    playoff_12_wins = delete_loser(playoff_12_wins, record['driver_name'])
                elif current_race <= 35:
                    playoff_8_wins[record['driver_name']] = playoff_8_wins.get(record['driver_name'], 0) - 1
                    playoff_8_wins = delete_loser(playoff_8_wins, record['driver_name'])
    return season_points, playoff_points, season_wins, playoff_16_wins, playoff_12_wins, playoff_8_wins

def delete_loser(wins_dist, driver):
    if wins_dist[driver] == 0:
        del wins_dist[driver]
    return wins_dist
