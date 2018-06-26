from app.app import app
import pytest


@pytest.fixture(scope="module")
def app_setup():
    app.config['DEFAULT_DB'] = 'tests'
    with app.app_context():
        yield app
