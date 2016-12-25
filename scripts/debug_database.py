from datetime import datetime, date, time
import os
import sys


##########################################
# 3rd party modules
###########################################
import googlemaps
import ipdb
from IPython import embed
from timezonefinder import TimezoneFinder

##########################################
# setup configuration and path for imports
###########################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_dir)

##########################################
# Import the run components
##########################################
from run import db
from run.lib import convert_to_degrees, speed, dist, split, elevation, find_timezone, reverse_geocode
from run.models import Timezone, Country, State, City, Day, Run, Race

FORECAST_API_KEY='8261b9ec237c8876cbd21d05c6447452'
GOOGLE_API_KEY='AIzaSyCBFTk2JuESrKlpab-LYNwG56zXI6eUka8'

tf = TimezoneFinder()
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

lat = convert_to_degrees(559289458)
lng = convert_to_degrees(-1360110105)

location = reverse_geocode(gmaps,lat,lng)
cur_tz = Timezone(name=find_timezone(tf,lat,lng))

us = Country(name=location['country'])

mt = State(name=location['state'])
#mt = State(name='Montana', country=us)

msla = City(name=location['city'])
#msla = City(name='Missoula', state=mt)

mon = Day(sunrise=time(0,26,0), sunset=time(2,59,0), date=date(2016,8,8))

run = Run(avg_speed=2.51,
          max_speed=3.228,
          start_position_lat=convert_to_degrees(559289458),
          start_position_long=convert_to_degrees(-1360110105),
          end_position_lat=convert_to_degrees(-1360110105),
          end_position_long=convert_to_degrees(-1359922776),
          total_ascent=234,
          total_descent=234,
          total_distance=5.02,
          start_time=datetime(2016,8,8,12,5,5),
          total_timer_time=550398,
          state=mt,
          total_elapsed_time=550398,
          city=msla,
          country=us,
          timezone=cur_tz,
          #timezone=mst,
          day=mon,
          )

#db.session.add_all([cur_tz, us, mt, msla, mon, run])
#db.session.commit()

embed(header='post-record creation, pre-record submission')
#ipdb.set_trace()
