from exaged.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Devis(Base):
    __tablename__ = 'devis'
    id = Column(Integer, primary_key=True)
    exact_quotation_id = Column(String(255), unique=True)
    exact_quotation_number = Column(Integer)
    exact_tier_id = Column(String(255), ForeignKey('tier.exact_id'))
    exact_your_ref = Column(String(255))
    tier = relationship("Tier")

