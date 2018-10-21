from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from traces_api.database import Base


class ModelAnnotatedUnit(Base):

    __tablename__ = "annotated_unit"

    id_annotated_unit = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(4096), nullable=False)
    id_author = Column(Integer(), nullable=False)
    creation_time = Column(DateTime, nullable=False)
    stats = Column(String(4096))
    ip_mapping = Column(String(255), nullable=False)
    file_location = Column(String(255), nullable=False)


class ModelAnnotatedUnitLabel(Base):

    __tablename__ = "annotated_unit_label"

    id_annotated_unit = Column(
        Integer(),
        ForeignKey('annotated_unit.id_annotated_unit', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    label = Column(String(32), primary_key=True)

