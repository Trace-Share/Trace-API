import json
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from traces_api.database import Base


class ModelAnnotatedUnit(Base):

    __tablename__ = "annotated_unit"

    id_annotated_unit = Column(BigInteger(), primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(4096), nullable=False)
    creation_time = Column(DateTime, nullable=False)
    stats = Column(Text())
    ip_details = Column(Text(), nullable=False)
    file_location = Column(String(255), nullable=False)

    labels = relationship("ModelAnnotatedUnitLabel", cascade="all,delete,delete-orphan")

    def dict(self):
        return dict(
            id_annotated_unit=self.id_annotated_unit,
            name=self.name,
            description=self.description,
            creation_time=self.creation_time,
            stats=json.loads(self.stats) if self.stats else None,
            ip_details=json.loads(self.ip_details) if self.ip_details else None,
            file_location=self.file_location,
            labels=[label.label for label in self.labels],
        )


class ModelAnnotatedUnitLabel(Base):

    __tablename__ = "annotated_unit_label"

    id_annotated_unit = Column(
        BigInteger(),
        ForeignKey('annotated_unit.id_annotated_unit', ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True
    )
    label = Column(String(32), primary_key=True)

