from exaged.model import Base
from exaged.model.tier import Tier
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
    exact_status = Column(Integer)
    exact_status_description = Column(String(255))
    tier = relationship(Tier, uselist=False)

    def to_json(self):
        return {
            'id': self.exact_order_id,
            'description': self.exact_order_description,
            'order_number': self.exact_order_number,
            'status_description': self.exact_status_description,
            'status': self.exact_status
        }
