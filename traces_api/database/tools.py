from . import Base

from .model.unit import ModelUnit
from .model.annotated_unit import ModelAnnotatedUnit, ModelAnnotatedUnitLabel
from .model.mix import ModelMix, ModelMixFileGeneration, ModelMixLabel, ModelMixOrigin


"""
List of all tables used in application
"""
TABLES = [
    ModelUnit.__table__,
    ModelAnnotatedUnit.__table__,
    ModelAnnotatedUnitLabel.__table__,
    ModelMix.__table__,
    ModelMixLabel.__table__,
    ModelMixOrigin.__table__,
    ModelMixFileGeneration.__table__,
]


def create_database(engine):
    """
    Create database schema if not exists
    :param engine: sqlalchemy engine
    :return:
    """
    Base.metadata.create_all(engine, tables=TABLES)


def recreate_database(engine):
    """
    Drop all known database tables and create them from scratch
    :param engine: sqlalchemy engine
    """
    Base.metadata.drop_all(engine, tables=TABLES)
    Base.metadata.create_all(engine, tables=TABLES)
