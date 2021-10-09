from datetime import datetime

from exaged.model import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class Tier(Base):
    __tablename__ = "tier"
    id = Column(Integer, primary_key=True)
    exact_id = Column(String(255), unique=True)
    exact_account_code = Column(String(255))
    exact_name = Column(String(255))
    exact_is_supplier = Column(Boolean)
    exact_is_reseller = Column(Boolean)
    exact_is_sales = Column(Boolean)
    exact_is_purchase = Column(Boolean)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
