from exaged.model import Base
from sqlalchemy import Column, String, TIMESTAMP


class LastSyncSuccess(Base):
    __tablename__ = "last_sync_success"
    sync_type = Column(String(255), primary_key=True)
    timestamp = Column(TIMESTAMP)
