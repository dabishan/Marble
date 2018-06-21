#######################
# Contain Flask and Initilization
from flask import Flask
import logging

# Initialize Flask App
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Set up Logging
with app.app_context():
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s (%(funcName)s: %(lineno)d)'))
    file_handler.setLevel(app.config['DEBUG_LEVEL'])
    app.logger.addHandler(file_handler)


