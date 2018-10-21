import pytest

from app import create_engine, setup_database

from traces_api.database.tools import recreate_database


@pytest.fixture()
def database_url():
    return "postgresql://root:example@localhost/traces"


@pytest.fixture(scope="function")
def sqlalchemy_session(database_url):
    engine = create_engine(database_url)
    session = setup_database(engine)

    recreate_database(engine)

    return session
