import os
import datetime
from sys import platform
from pathlib import Path

import pandas as pd

from objects import CurrentWaypoint, TideWaypoint
import requests
from bs4 import BeautifulSoup as Soup
import json

from tt_chrome_driver import chrome_driver

profile_lookup = {'darwin': 'HOME', 'win32': 'USERPROFILE'}

if __name__ == '__main__':

    # ---------- CHECK CHROME ----------
    chrome_driver.check_driver()
    if chrome_driver.latest_stable_version > chrome_driver.installed_driver_version:
        chrome_driver.install_stable_driver()

    print(f'\nProcessing current stations')

    east_coast_current_stations = 'https://tidesandcurrents.noaa.gov/noaacurrents/Stations?g=444'
    current_waypoints = Path(str(os.environ[profile_lookup[platform]]) + '/Developer Workspace/GPX/NOAA Current Stations/')
    os.makedirs(current_waypoints, exist_ok=True)
    current_request = requests.get(east_coast_current_stations)

    tree = Soup(current_request.text, 'html.parser')
    for tag in tree.find_all('a'):
        if 'Predictions?' in str(tag.get('href')):
            wp = CurrentWaypoint(tag)
            wp.write_me(current_waypoints)

    print(f'\nProcessing tide stations')

    east_coast_tide_stations_url = 'https://tidesandcurrents.noaa.gov/tide_predictions.html?gid=1746#listing'
    tide_waypoints = Path(str(os.environ[profile_lookup[platform]]) + '/Developer Workspace/GPX/NOAA Tide Stations/')
    os.makedirs(tide_waypoints, exist_ok=True)
    chrome_driver.set_driver()
    tide_source = chrome_driver.page_source(east_coast_tide_stations_url)

    tree = Soup(tide_source, 'html.parser')
    for tag in tree.find_all('a'):
        if 'noaatidepredictions.html?' in str(tag):
            row_list = [str(d.text).strip() for d in tag.find_parent('tr').children]
            wp = TideWaypoint(row_list)
            wp.write_me(tide_waypoints)

    # ---------- Moon Phases ----------
    # https://aa.usno.navy.mil/data/api#rstt documentation
    print('\nProcessing sun moon data for East River')
    frame = pd.DataFrame(columns=['date', 'phase'])
    start_year = 2023
    brooklyn_bridge_coords = "40.706, -73.9977"
    sun_moon_folder = Path(str(os.environ[profile_lookup[platform]]) + '/Developer Workspace/ER_' + str(start_year) + '/Transit Time')
    sun_moon_file = 'sun_moon.csv'
    os.makedirs(sun_moon_folder, exist_ok=True)

    for year in range(start_year, start_year+4):
        date = datetime.datetime(year, 1, 1)
        print(year, date.year, date)

        while date.year < start_year + 1:
            sun_moon_url = "https://aa.usno.navy.mil/api/rstt/oneday?date=" + str(date.date()) + "&coords=" + brooklyn_bridge_coords
            sun_moon_request = requests.get(sun_moon_url)
            data = json.loads(sun_moon_request.text)
            frame.loc[len(frame)] = [str(date.date()), data['properties']['data']['curphase']]
            print(str(date.date().month))
            date = date + datetime.timedelta(days=1)

        frame.to_csv(sun_moon_folder.joinpath(sun_moon_file), index=False)
