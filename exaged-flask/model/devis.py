from datetime import datetime

from exaged.model import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Devis(Base):
    __tablename__ = "devis"
    id = Column(Integer, primary_key=True)
    exact_quotation_id = Column(String(255), unique=True)
    exact_quotation_number = Column(Integer)
    exact_tier_id = Column(String(255), ForeignKey("tier.exact_id"))
    exact_your_ref = Column(String(255))
    exact_order_description = Column(String(255))
    tier = relationship("Tier")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
