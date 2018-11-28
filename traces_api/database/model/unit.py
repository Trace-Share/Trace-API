from sqlalchemy import Column, Integer, String, DateTime
from traces_api.database import Base


class ModelUnit(Base):

    __tablename__ = 'unit'

    id_unit = Column(Integer(), primary_key=True, autoincrement=True)
    creation_time = Column(DateTime, nullable=False)
    last_update_time = Column(DateTime, nullable=False)
    annotation = Column(String(255))
    ip_mac_mapping = Column(String(255))
    uploaded_file_location = Column(String(255), nullable=False)
