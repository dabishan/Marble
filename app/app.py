#######################
# Contain Flask and Initilization
from flask import Flask, render_template
import logging
import os

# Initialize Flask App
BASE_URL = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder=BASE_URL + "/www/templates/", static_folder=BASE_URL + "/www/dist/", static_url_path='')
app.config.from_pyfile('config.py')

# Set up Logging
with app.app_context():
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s (%(funcName)s: %(lineno)d)'))
    file_handler.setLevel(app.config['DEBUG_LEVEL'])
    app.logger.addHandler(file_handler)


#import routes
from app.routes import *