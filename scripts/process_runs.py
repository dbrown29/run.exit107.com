import argparse
from datetime import datetime, date, time
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
from run import db
from run.lib import convert_to_degrees, speed, dist, split, elevation, find_timezone, reverse_geocode
from run.models import Timezone, Country, State, City, Day, Run, Race

##########################################
# These will eventually be handled in the config file
###########################################
FORECAST_API_KEY='8261b9ec237c8876cbd21d05c6447452'
GOOGLE_API_KEY='AIzaSyCBFTk2JuESrKlpab-LYNwG56zXI6eUka8'

##########################################
# Open the file named on the command line
###########################################
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

##########################################
# Build our api instance
##########################################
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
tf = TimezoneFinder()

##########################################
# Some tracking variables
##########################################
moments = []
initial=True

##########################################
# Start processing the file
##########################################
for i, record in enumerate(fit_file.messages):
  if record.mesg_num == 20:
    #############################################
    # Get the location data. We'll move to the next record if the location information is bad.
    #############################################
    lat = convert_to_degrees(record.get_value('position_lat'))
    lng = convert_to_degrees(record.get_value('position_long'))
    if lat and lng:
      timezone = find_timezone(tf,lat,lng)
    else:
      print('Bad Location Data')
      next

    #############################################
    # Get the time data
    #############################################
    # store in utc, we'll convert later. This is just easier and allows for more flexibility.
    print(record.get_value('timestamp'))
    print(type(record.get_value('timestamp')))
    utc_time = pendulum.instance(record.get_value('timestamp'))
    # local is for weather only
    local_tz = pendulum.timezone(timezone)
    local_time = local_tz.convert(utc_time)

    if (local_time.hour,local_time.minute) not in moments:
      moments.append((local_time.hour,local_time.minute))

      #############################################
      # Get the location data.
      #############################################
      location = reverse_geocode(gmaps,lat,lng)

      #############################################
      # Get the weather/sunrise/sunset data
      #############################################
      uri = 'https://api.forecast.io/forecast/{api_key}/{lat},{lng},{time}'.format(
            api_key=FORECAST_API_KEY,
            time=local_time.isoformat(),
            lat=lat,
            lng=lng)

      resp = requests.get(uri)
      weather = json.loads(resp.text)

      #############################################
      # First record to establish some daily data
      #############################################
      if initial:
        # These are all UTC.
        sunrise = pendulum.from_timestamp(weather['daily']['data'][0]['sunriseTime'])
        sunset = pendulum.from_timestamp(weather['daily']['data'][0]['sunsetTime'])

        day = Day(sunrise=sunrise, sunset=sunset, date=utc_time.date())

        country = Country(name=location['country'])
        state = State(name=location['state'])
        #mt = State(name='Montana', country=us)
        city = City(name=location['city'])
        #msla = City(name='Missoula', state=mt)

        import ipdb
        ipdb.set_trace()

        initial = False

# Now we begin processing in earnst
# First find the first record, this is our start time
# Now record all points, those will be linked to the run...?
# Watch for stop times initiated by lap events, those are obviously mile laps that will be linked to the run
# Watch for stop times initiated by "manual" events. That's either a full stop time or a watch stop time
# Final stop time "manual" is the end of our run.

#    try:
#      run = Run(avg_speed=2.51,
#                max_speed=3.228,
#                start_position_lat=convert_to_degrees(559289458),
#                start_position_long=convert_to_degrees(-1360110105),
#                end_position_lat=convert_to_degrees(-1360110105),
#                end_position_long=convert_to_degrees(-1359922776),
#                total_ascent=234,
#                total_descent=234,
#                total_distance=5.02,
#                start_time=datetime(2016,8,8,12,5,5),
#                total_timer_time=550398,
#                state=location['state'],
#                total_elapsed_time=550398,
#                city=location['city'],
#                country=location{'country'],
#                timezone=cur_tz,
#                #timezone=mst,
#                day=mon,
#                )
#      db.session.add(run)
#      db.session.flush()
#    except IntegrityError:
#      db.session.rollback()
#      cur_year=Run.query.filter_by(start_time=year).first()
#    db.session.commit()
#
#
#
#
#  run = Run(avg_speed=2.51,
#            max_speed=3.228,
#            start_position_lat=convert_to_degrees(559289458),
#            start_position_long=convert_to_degrees(-1360110105),
#            end_position_lat=convert_to_degrees(-1360110105),
#            end_position_long=convert_to_degrees(-1359922776),
#            total_ascent=234,
#            total_descent=234,
#            total_distance=5.02,
#            start_time=datetime(2016,8,8,12,5,5),
#            total_timer_time=550398,
#            state=mt,
#            total_elapsed_time=550398,
#            city=msla,
#            country=us,
#            timezone=cur_tz,
#            #timezone=mst,
#            day=mon,
#            )
#
#  #db.session.add_all([cur_tz, us, mt, msla, mon, run])
#  #db.session.commit()
#
#  embed(header='post-record creation, pre-record submission')
#  #ipdb.set_trace()
#
#              datetime=local_time.strftime('%Y-%m-%D %H:%M:%S'),
#              #datetime=local_time.to_day_datetime_string(),
#              timezone=timezone,
#              temp=weather.get('currently')['temperature'],
#              #temp=50,
#              lat=lat,
#              lng=lng,
#              city=location['city'],
#              state=location['state'],
#              country=location['country'],
#              dist=dist(record.get_value('distance')),
#              elevation=elevation(record.get_value('altitude')),
#              speed=speed(record.get_value('speed')),
#              split=split(record.get_value('speed'))
#              )
#        )
#        print('#'*50,'\n')
#  for year in years:
#    try:
#      cur_year=Year(year=year)
#      db.session.add(cur_year)
#      db.session.flush()
#    except IntegrityError:
#      db.session.rollback()
#      cur_year=Year.query.filter_by(year=year).first()
#    db.session.commit()
