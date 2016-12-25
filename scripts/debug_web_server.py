import os
import sys

##########################################
# setup configuration and path for imports
###########################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_dir)

from run import run_app
from run.lib import convert_to_degrees, speed, dist, split, elevation, find_timezone, reverse_geocode
from run.models import Timezone, Country, State, City, Day, Run, Race

from werkzeug import SharedDataMiddleware

# serve the static files from flask for dev work
run_app.wsgi_app = SharedDataMiddleware(run_app.wsgi_app, {
  '/': os.path.join(os.path.dirname(__file__), '/static')
})

run_app.debug = True
run_app.run(host='0.0.0.0', port=5050)
