from . import Base

from .model.unit import ModelUnit
from .model.annotated_unit import ModelAnnotatedUnit, ModelAnnotatedUnitLabel
from .model.mix import ModelMix, ModelMixFileGeneration, ModelMixLabel, ModelMixOrigin


TABLES = [
    ModelUnit.__table__,
    ModelAnnotatedUnit.__table__,
    ModelAnnotatedUnitLabel.__table__,
    ModelMix.__table__,
    ModelMixLabel.__table__,
    ModelMixOrigin.__table__,
    ModelMixFileGeneration.__table__,
]


def recreate_database(engine):
    """
    Drop all known database tables and create them from scratch
    :param engine: sqlalchemy engine
    """
    Base.metadata.drop_all(engine, tables=TABLES)
    Base.metadata.create_all(engine, tables=TABLES)
