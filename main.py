import os
from sys import platform
from pathlib import Path
from objects import CurrentWaypoint, TideWaypoint
import requests
from bs4 import BeautifulSoup as Soup

from tt_chrome_driver import chrome_driver

profile_lookup = {'darwin': 'HOME', 'win32': 'USERPROFILE'}

if __name__ == '__main__':

    east_coast_current_stations = 'https://tidesandcurrents.noaa.gov/noaacurrents/Stations?g=444'
    current_waypoints = Path(str(os.environ[profile_lookup[platform]]) + '/Developer Workspace/GPX/NOAA Current Stations/')
    os.makedirs(current_waypoints, exist_ok=True)
    current_request = requests.get(east_coast_current_stations)

    tree = Soup(current_request.text, 'html.parser')
    for tag in tree.find_all('a'):
        if 'Predictions?' in str(tag.get('href')):
            wp = CurrentWaypoint(tag)
            wp.write_me(current_waypoints)

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
