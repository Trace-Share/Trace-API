import pytest

from app import FlaskApp


@pytest.fixture
def app(sqlalchemy_session):
    app = FlaskApp(sqlalchemy_session).create_app()
    return app
