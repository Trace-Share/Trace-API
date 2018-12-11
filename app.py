import sqlalchemy
import sqlalchemy.orm

from flask import Flask, Blueprint
from flask_injector import FlaskInjector

from traces_api.api.restplus import api
from traces_api.database.tools import recreate_database

from traces_api.modules.dataset.controller import ns as dataset_namespace
from traces_api.modules.annotated_unit.controller import ns as annotated_unit_namespace
from traces_api.modules.mix.controller import ns as mix_namespace

from traces_api.tools import TraceAnalyzer, TraceNormalizer, TraceMixing


def create_engine(url):
    engine = sqlalchemy.create_engine(url)
    return engine


def setup_database(engine):
    session = sqlalchemy.orm.sessionmaker(bind=engine)()

    return session


def setup_databasea(url):
    engine = create_engine(url)
    session = setup_database(engine)

    recreate_database(engine)

    return session


class FlaskApp:

    def __init__(self, session):
        self._session = session

    @staticmethod
    def init_app(flask_app):
        blueprint = Blueprint('api', __name__)
        api.init_app(blueprint)

        api.add_namespace(dataset_namespace)
        api.add_namespace(annotated_unit_namespace)
        api.add_namespace(mix_namespace)

        flask_app.register_blueprint(blueprint)

    def configure(self, binder):
        from traces_api.modules.dataset.service import UnitService
        from traces_api.modules.annotated_unit.service import AnnotatedUnitService
        from traces_api.modules.mix.service import MixService
        from traces_api.storage import FileStorage

        annotated_unit_service = AnnotatedUnitService(self._session, FileStorage(storage_folder="storage/ann_units"), TraceAnalyzer(), TraceNormalizer())

        unit_service = UnitService(
            self._session, annotated_unit_service, FileStorage(storage_folder="storage/units"), TraceAnalyzer()
        )

        mix_service = MixService(
            self._session, annotated_unit_service, FileStorage(storage_folder="storage/mixes"), TraceNormalizer(), TraceMixing()
        )

        binder.bind(UnitService, to=unit_service)
        binder.bind(AnnotatedUnitService, to=annotated_unit_service)
        binder.bind(MixService, to=mix_service)

    def create_app(self):
        app = Flask(__name__)
        self.init_app(app)

        FlaskInjector(app=app, modules=[self.configure])

        return app


def run():
    session = setup_databasea("postgresql://root:example@localhost/traces")
    # session = setup_databasea("sqlite://")

    app = FlaskApp(session).create_app()
    app.run(debug=True)


if __name__ == "__main__":
    run()

