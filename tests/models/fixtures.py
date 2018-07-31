from app.app import app
import pytest


@pytest.fixture(scope="module")
def app_setup():
    app.config['DEFAULT_DB'] = 'tests'
    app.config['SALT'] = "$2b$08$duvTxgV7EW9s98pmpFgRAO"
    with app.app_context():
        yield app
