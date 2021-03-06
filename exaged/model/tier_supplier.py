from exaged.model import Base
from sqlalchemy import Column, Integer, String


class TierSupplier(Base):
    __tablename__ = 'tier_supplier'
    id = Column(Integer, primary_key=True)
    exact_id = Column(String(255), unique=True)
    prefixed_account_code = Column(String(255))
    exact_name = Column(String(255))
