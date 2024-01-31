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
    frame = pd.DataFrame(columns=['start_date', 'phase', 'fracillum', 'name'])
    brooklyn_bridge_coords = "40.706, -73.9977"
    sun_moon_folder = Path(str(os.environ[profile_lookup[platform]]) + '/Developer Workspace')
    filepath = sun_moon_folder.joinpath('sun_moon.csv')
    os.makedirs(sun_moon_folder, exist_ok=True)
    print(f'     Processing {filepath}')

    cal_year = 2024

    day = datetime.datetime(cal_year - 1, 12, 1)
    while day.year == cal_year - 1:
        sun_moon_request = None
        sun_moon_url = "https://aa.usno.navy.mil/api/rstt/oneday?date=" + str(day.date()) + "&coords=" + brooklyn_bridge_coords
        try:
            sun_moon_request = requests.get(sun_moon_url)
        except requests.Timeout:
            try:
                sun_moon_request = requests.get(sun_moon_url)
            except requests.Timeout:
                print(f'requests Timeout err, 2nd try')

        data = json.loads(sun_moon_request.text)
        phase = data['properties']['data']['curphase']
        fracillum = data['properties']['data']['fracillum']
        phase_num = round(int(fracillum[:-1])/11.11)
        phase_num = phase_num * -1 if "Waning" in phase and not phase_num == 9 else phase_num
        name = 'moon ' + str(phase_num)
        print(day, phase, fracillum, name)
        frame.loc[len(frame)] = [str(day.date()), phase, fracillum, name]
        day = day + datetime.timedelta(days=1)

    day = datetime.datetime(cal_year, 1, 1)
    while day.year == cal_year:
        sun_moon_request = None
        sun_moon_url = "https://aa.usno.navy.mil/api/rstt/oneday?date=" + str(day.date()) + "&coords=" + brooklyn_bridge_coords
        try:
            sun_moon_request = requests.get(sun_moon_url)
        except requests.Timeout:
            try:
                sun_moon_request = requests.get(sun_moon_url)
            except requests.Timeout:
                print(f'requests Timeout err, 2nd try')

        data = json.loads(sun_moon_request.text)
        phase = data['properties']['data']['curphase']
        fracillum = data['properties']['data']['fracillum']
        phase_num = round(int(fracillum[:-1]) / 11.11)
        phase_num = phase_num * -1 if "Waning" in phase and not phase_num == 9 else phase_num
        name = 'moon ' + str(phase_num)
        print(day, phase, fracillum, name)
        frame.loc[len(frame)] = [str(day.date()), phase, fracillum, name]
        day = day + datetime.timedelta(days=1)

    day = datetime.datetime(cal_year + 1, 1, 1)
    while day.month == 1:
        sun_moon_request = None
        sun_moon_url = "https://aa.usno.navy.mil/api/rstt/oneday?date=" + str(day.date()) + "&coords=" + brooklyn_bridge_coords
        try:
            sun_moon_request = requests.get(sun_moon_url)
        except requests.Timeout:
            try:
                sun_moon_request = requests.get(sun_moon_url)
            except requests.Timeout:
                print(f'requests Timeout err, 2nd try')

        data = json.loads(sun_moon_request.text)
        phase = data['properties']['data']['curphase']
        fracillum = data['properties']['data']['fracillum']
        phase_num = round(int(fracillum[:-1]) / 11.11)
        phase_num = phase_num * -1 if "Waning" in phase and not phase_num == 9 else phase_num
        name = 'moon ' + str(phase_num)
        print(day, phase, fracillum, name)
        frame.loc[len(frame)] = [str(day.date()), phase, fracillum, name]
        day = day + datetime.timedelta(days=1)

        frame.to_csv(filepath, index=False)
