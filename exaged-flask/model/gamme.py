from exaged.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from datetime import datetime


class Gamme(Base):
    __tablename__ = "gamme"
    id = Column(Integer, primary_key=True)
    exact_item_id = Column(String(255), ForeignKey("article.exact_id"))
    exact_value = Column(String(255))
    exact_modified = Column(DateTime)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
