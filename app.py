import sqlalchemy

from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint

from traces_api.api.restplus import api
from traces_api.database.tools import recreate_database

from traces_api.modules.dataset.controller import ns as dataset_namespace

app = Flask(__name__)


def create_engine(url):
    engine = sqlalchemy.create_engine(url)
    return engine


def setup_database(engine):
    session = sessionmaker(bind=engine)()

    return session


def init_app(flask_app):
    blueprint = Blueprint('api', __name__)
    api.init_app(blueprint)

    api.add_namespace(dataset_namespace)

    flask_app.register_blueprint(blueprint)


def setup_databasea(url):
    engine = create_engine(url)
    session = setup_database(engine)

    recreate_database(engine)

    return session


if __name__ == "__main__":
    setup_databasea("postgresql://root:example@localhost/traces")

    init_app(app)
    app.run(debug=True)
