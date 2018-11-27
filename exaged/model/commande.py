from exaged.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Commande(Base):
    __tablename__ = 'commande'
    id = Column(Integer, primary_key=True)
    exact_order_id = Column(String(255), unique=True)
    exact_tier_id = Column(String(255), ForeignKey('tier.exact_id'))
    exact_order_description = Column(String(255))
    exact_your_ref = Column(String(255))
    exact_order_number = Column(Integer)
    tier = relationship("Tier")

