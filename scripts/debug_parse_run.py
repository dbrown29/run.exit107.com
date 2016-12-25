import argparse
import sys
import os
import sys

from fitparse import FitFile, FitParseError
import googlemaps
import json
from path import Path
import pendulum
import requests
from timezonefinder import TimezoneFinder

##########################################
# setup configuration and path for imports
###########################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_dir)

##########################################
# import run libraries
###########################################
from run.lib import convert_to_degrees, speed, dist, split, elevation, find_timezone, reverse_geocode

FORECAST_API_KEY='8261b9ec237c8876cbd21d05c6447452'
GOOGLE_API_KEY='AIzaSyCBFTk2JuESrKlpab-LYNwG56zXI6eUka8'
# We don't really use WU anymore
#WEATHERUNDERGROUND_API_KEY='01c440c2fae9b2b2'

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('file', type=argparse.FileType('r'), nargs=1,
                    help='File to be parsed (.fit)')

args = parser.parse_args()

input_file_path = Path(args.file[0].name)

with open(input_file_path, 'rb') as input_file:
  try:
    fit_file = FitFile(input_file, check_crc=False)
    fit_file.parse()
  except FitParseError as err:
    print('Error while parsing {}: {}'.format(input_file.relpath(), err))
    sys.exit(1)

# Build our api instances
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
tf = TimezoneFinder()

moments = []
j=0
for i, record in enumerate(fit_file.messages):
  if record.mesg_num == 20:
    lat = convert_to_degrees(record.get_value('position_lat'))
    lng = convert_to_degrees(record.get_value('position_long'))
    if lat and lng:
      timezone = find_timezone(tf,lat,lng)
      location = reverse_geocode(gmaps,lat,lng)
    else:
      next

    utc_time = pendulum.instance(record.get_value('timestamp'))
    local_tz = pendulum.timezone(timezone)
    local_time = local_tz.convert(utc_time)

    if (local_time.hour,local_time.minute) not in moments:
      moments.append((local_time.hour,local_time.minute))

      uri = 'https://api.forecast.io/forecast/{api_key}/{lat},{lng},{time}'.format(
            api_key=FORECAST_API_KEY,
            time=local_time.isoformat(),
            lat=lat,
            lng=lng)

      resp = requests.get(uri)
      weather = json.loads(resp.text)

# Google Elevation API
# I think I'm going to trust the watch instead
#      uri = 'https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={api_key}'.format(
#            api_key=GOOGLE_API_KEY,
#            lat=lat,
#            lng=lng)
#      resp = requests.get(uri)
#      g_elevation = json.loads(resp.text)

      print('#'*50)
      print('datetime: {datetime}\ntimezone: {timezone}\ntemp: {temp}\nlocation: {lat},{lng}\ncity: {city}\nstate: {state}\ncountry: {country}\ndistance: {dist} mi\nelevation: {elevation} ft\nspeed: {speed} mph\nsplit: {split} minute miles'.format(
            datetime=local_time.strftime('%Y-%m-%D %H:%M:%S'),
            #datetime=local_time.to_day_datetime_string(),
            timezone=timezone,
            temp=weather.get('currently')['temperature'],
            #temp=50,
            lat=lat,
            lng=lng,
            city=location['city'],
            state=location['state'],
            country=location['country'],
            dist=dist(record.get_value('distance')),
            elevation=elevation(record.get_value('altitude')),
            speed=speed(record.get_value('speed')),
            split=split(record.get_value('speed'))
            )
      )
      print('#'*50,'\n')