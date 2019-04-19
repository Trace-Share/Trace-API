import pytest

from app import create_engine, setup_database

from traces_api.database.tools import recreate_database
from traces_api.config import Config
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def config():
    return Config("config_tests.ini")


@pytest.fixture()
def database_url(config):
    return config.get("database", "connection_string")


@pytest.fixture()
def sqlalchemy_engine(database_url):
    params = {}
    if database_url.startswith("sqlite"):
        params["connect_args"] = {'check_same_thread': False}
        params["poolclass"] = StaticPool

    engine = create_engine(database_url, **params)

    return engine


@pytest.fixture(scope="function")
def sqlalchemy_session(sqlalchemy_engine):
    session = setup_database(sqlalchemy_engine)

    recreate_database(sqlalchemy_engine)

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def file_hydra_1_binary():
    with open("tests/fixtures/hydra-1_tasks.pcap", "rb") as f:
        return f.read()
