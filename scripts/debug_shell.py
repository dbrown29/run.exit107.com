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
#*****************************************
# this should pull the keys from the config defined in run_app
#*****************************************
##########################################

FORECAST_API_KEY='8261b9ec237c8876cbd21d05c6447452'
GOOGLE_API_KEY='AIzaSyCBFTk2JuESrKlpab-LYNwG56zXI6eUka8'
WEATHERUNDERGROUND_API_KEY='01c440c2fae9b2b2'

##########################################
# setup configuration and path for imports
###########################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_dir)

##########################################
# Import the application components
##########################################
from run import run_app
from run import db
from run.lib import convert_to_degrees, speed, dist, split, elevation, find_timezone, reverse_geocode
from run.models import Timezone, Country, State, City, Day, Run, Race

##########################################
# Create a sample
##########################################

##########################################
## Start the ipython shell
##########################################
from IPython import embed
embed()
