from datetime import datetime

from exaged.model import Base
from exaged.model.gamme import Gamme
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class Article(Base):

    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    exact_id = Column(String(255), unique=True)

    exact_code = Column(String(255))
    exact_description = Column(String(255))

    exact_modified = Column(DateTime)

    gamme = relationship(Gamme, uselist=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
