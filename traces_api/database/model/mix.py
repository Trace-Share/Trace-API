from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean

from traces_api.database import Base


class ModelMix(Base):

    __tablename__ = "mix"

    id_mix = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(4096), nullable=False)
    id_author = Column(Integer(), nullable=False)
    creation_time = Column(DateTime, nullable=False)
    stats = Column(String(4096))


class ModelMixLabel(Base):

    __tablename__ = "mix_label"

    id_mix = Column(
        Integer(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    label = Column(String(32), primary_key=True)


class ModelMixOrigin(Base):

    __tablename__ = "mix_origin"

    id_mix = Column(
        Integer(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    id_annotated_unit = Column(
        Integer(),
        ForeignKey('annotated_unit.id_annotated_unit', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    ip_mac_mapping = Column(String(255))
    timestamp = Column(Integer())


class ModelMixFileGeneration(Base):

    __tablename__ = "mix_file_generation"

    id_mix_generation = Column(Integer(), primary_key=True, autoincrement=True)
    id_mix = Column(
        Integer(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    creation_time = Column(DateTime, nullable=False)
    file_location = Column(String(255), nullable=False)
    expired = Column(Boolean(), nullable=False)
    progress = Column(Integer(), nullable=False)
