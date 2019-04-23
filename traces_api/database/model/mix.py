from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship

from traces_api.database import Base


class ModelMix(Base):

    __tablename__ = "mix"

    id_mix = Column(BigInteger(), primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(4096), nullable=False)
    creation_time = Column(DateTime, nullable=False)
    stats = Column(String(4096))

    labels = relationship("ModelMixLabel", cascade="all,delete,delete-orphan")
    origins = relationship("ModelMixOrigin", cascade="all,delete")

    def dict(self):
        return dict(
            id_mix=self.id_mix,
            name=self.name,
            description=self.description,
            creation_time=self.creation_time,
            labels=[label.label for label in self.labels],
            ids_annotated_unit=[o.id_annotated_unit for o in self.origins],
        )


class ModelMixLabel(Base):

    __tablename__ = "mix_label"

    id_mix = Column(
        BigInteger(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    label = Column(String(32), primary_key=True)


class ModelMixOrigin(Base):

    __tablename__ = "mix_origin"

    id_mix = Column(
        BigInteger(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    id_annotated_unit = Column(
        BigInteger(),
        ForeignKey('annotated_unit.id_annotated_unit', ondelete="RESTRICT", onupdate="RESTRICT"),
        primary_key=True
    )
    ip_mapping = Column(String(4000))
    mac_mapping = Column(String(4000))
    timestamp = Column(Integer())


class ModelMixFileGeneration(Base):

    __tablename__ = "mix_file_generation"

    id_mix_generation = Column(BigInteger(), primary_key=True, autoincrement=True)
    id_mix = Column(
        BigInteger(),
        ForeignKey('mix.id_mix', ondelete="CASCADE", onupdate="RESTRICT"),
        index=True
    )
    creation_time = Column(DateTime, nullable=False)
    file_location = Column(String(255), nullable=True)
    expired = Column(Boolean(), nullable=False)
    progress = Column(Integer(), nullable=False)
