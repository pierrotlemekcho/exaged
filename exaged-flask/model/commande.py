from datetime import datetime

from exaged.constants import SHARE_ORDER_FOLDER
from exaged.model import Base
from exaged.model.ligne_de_commande import LigneDeCommande
from exaged.model.tier import Tier
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship


class Commande(Base):
    __tablename__ = "commande"
    id = Column(Integer, primary_key=True)
    exact_order_id = Column(String(255), unique=True)
    exact_tier_id = Column(String(255), ForeignKey("tier.exact_id"))
    exact_order_description = Column(String(255))
    exact_your_ref = Column(String(255))
    exact_order_number = Column(Integer)
    exact_status = Column(Integer)
    exact_status_description = Column(String(255))
    tier = relationship(Tier, uselist=False)
    exact_amount = Column(Numeric(precision=20, scale=3))
    exact_modified = Column(DateTime)
    lignes = relationship(LigneDeCommande, cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    def to_json(self):
        return {
            "id": self.exact_order_id,
            "description": self.exact_order_description,
            "order_number": self.exact_order_number,
            "status_description": self.exact_status_description,
            "status": self.exact_status,
            "lines": [ligne.to_json() for ligne in self.lignes],
            "client_name": self.tier.exact_name,
        }

    @property
    def folder_path(self):
        return f"{SHARE_ORDER_FOLDER}{self.tier.exact_name}/C{self.exact_order_number}/"
