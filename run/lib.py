import pendulum
import requests
from timezonefinder import TimezoneFinder

def timestamp_to_datetime(timestamp):
    utc_time = pendulum.instance(timestamp)
    return utc_time
  
def convert_to_degrees(coord):
  if coord:
    deg_coord = coord*(180/2**31)
    return deg_coord
  else:
    return None

#def convert_to_degrees(lat, lng):
#  if lat and lng:
#    deg_lat = lat*(180/2**31)
#    deg_lng = lng*(180/2**31)
#    return (deg_lat, deg_lng)
#  else:
#    return None

def speed(x):
  if x > 0:
    return round(x*2.236936,2)
  else:
    return 0

def dist(x):
  if x > 0:
    return round(x*0.00062137,2)
  else:
    return 0

def elevation(x):
  if x > 0:
    return round(x*3.281)
  else:
    return 0

def split(x):
  if x > 0:
    return round(60/(x*2.236936),2)
  else:
    return 0

def find_timezone(tf, lat, lng):
  lat = float(lat)
  lng = float(lng)

  try:
      timezone_name = tf.timezone_at(lng=lng, lat=lat)
      if timezone_name is None:
          timezone_name = tf.closest_timezone_at(lng=lng, lat=lat)
          # maybe even increase the search radius when it is still None

  except ValueError:
      print('no timezone found')
      # the coordinates were out of bounds
  return timezone_name

def reverse_geocode(gmap, lat, lng):
    reverse = gmap.reverse_geocode((lat, lng))
    for x in reverse[0]['address_components']:
      if 'locality' in x['types']:
        city = x['long_name']
      elif 'administrative_area_level_1' in x['types']:
        state = x['long_name']
      elif 'country' in x['types']:
        country = x['long_name']

    return {'city': city, 'state': state, 'country': country}

