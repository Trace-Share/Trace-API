import os.path
import sqlite3
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.event

from flask import Flask, Blueprint
from flask_injector import FlaskInjector

from traces_api.api.restplus import api
from traces_api.database.tools import recreate_database
from traces_api.config import Config

from traces_api.modules.dataset.controller import ns as dataset_namespace
from traces_api.modules.annotated_unit.controller import ns as annotated_unit_namespace
from traces_api.modules.mix.controller import ns as mix_namespace

from traces_api.tools import TraceAnalyzer, TraceNormalizer, TraceMixing
from traces_api.compression import Compression


APP_DIR = os.path.dirname(os.path.realpath(__file__))


def _fk_pragma_on_connect(dbapi_con, con_record):
    # Enable Foreign key support on SQLite db
    if isinstance(dbapi_con, sqlite3.Connection):
        dbapi_con.execute('pragma foreign_keys=ON')


def create_engine(url, **params):
    """
    Create sqlalchemy engine
    :param url: database connection url
    :param params: additional parameters
    :return: created engine
    """
    engine = sqlalchemy.create_engine(url, **params)
    sqlalchemy.event.listen(engine, 'connect', _fk_pragma_on_connect)
    return engine


def setup_database(engine):
    """
    Setup database session using session maker
    :param engine:
    :return:
    """
    session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = sqlalchemy.orm.scoped_session(session)
    return session


def prepare_database(url):
    """
    Prepare database session
    :param url: database connection url
    :return: sqlalchemy session_maker
    """

    engine = create_engine(url)
    session_maker = setup_database(engine)

    recreate_database(engine)

    return session_maker


class FlaskApp:
    """
    Configure Flask Application
    """

    def __init__(self, session_maker, config):
        """
        :param session_maker: Sqlalchemy session maker
        :param config: config
        """
        self._session_maker = session_maker
        self._config = config

    def init_app(self, flask_app):
        """
        Initialize appliaction

        :param flask_app:
        """

        @flask_app.teardown_request
        def teardown_request(exception):
            # Always rollback and cleanup transaction
            # All data should be already saved
            self._session_maker().rollback()

        blueprint = Blueprint('api', __name__)
        api.init_app(blueprint)

        api.add_namespace(dataset_namespace)
        api.add_namespace(annotated_unit_namespace)
        api.add_namespace(mix_namespace)

        flask_app.register_blueprint(blueprint)

    @staticmethod
    def _abs_storage_path(config_value):
        """
        Use absolute storage path

        :param config_value:
        :return: absolute path to folder
        """
        if config_value.startswith("/"):
            return config_value
        return "{}/{}".format(APP_DIR, config_value)

    def configure(self, binder):
        """
        Configure application, setup binder

        :param binder:
        """

        from traces_api.modules.dataset.service import UnitService
        from traces_api.modules.annotated_unit.service import AnnotatedUnitService
        from traces_api.modules.mix.service import MixService
        from traces_api.storage import FileStorage

        annotated_unit_storage = FileStorage(self._abs_storage_path(self._config.get("storage", "ann_units_dir")), compression=Compression())
        annotated_unit_service = AnnotatedUnitService(self._session_maker, annotated_unit_storage, TraceAnalyzer(), TraceNormalizer())

        unit_storage = FileStorage(self._abs_storage_path(self._config.get("storage", "units_dir")), compression=Compression())
        unit_service = UnitService(self._session_maker, annotated_unit_service, unit_storage, TraceAnalyzer())

        mix_storage = FileStorage(self._abs_storage_path(self._config.get("storage", "mixes_dir")), compression=Compression())
        mix_service = MixService(self._session_maker, annotated_unit_service, mix_storage, TraceNormalizer(), TraceMixing())

        binder.bind(UnitService, to=unit_service)
        binder.bind(AnnotatedUnitService, to=annotated_unit_service)
        binder.bind(MixService, to=mix_service)

    def create_app(self):
        """
        Create Flask application

        :return: flask application
        """
        app = Flask(__name__)
        self.init_app(app)

        FlaskInjector(app=app, modules=[self.configure])

        return app


def run():
    """
    Rum application
    """
    config = Config("config.ini")

    session = prepare_database(config.get("database", "connection_string"))

    app = FlaskApp(session, config).create_app()
    app.run(debug=True, port=int(config.get("app", "port")))


if __name__ == "__main__":
    run()

