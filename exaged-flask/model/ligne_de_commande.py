from datetime import datetime

from exaged.model import Base
from exaged.model.article import Article
from exaged.schema.order_line import OrderLineSchema
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship


class LigneDeCommande(Base):
    __tablename__ = "ligne_de_commande"
    id = Column(Integer, primary_key=True)
    exact_order_id = Column(String(255), ForeignKey("commande.exact_order_id"))
    exact_id = Column(String(255), unique=True)
    exact_item_id = Column(String(255), ForeignKey("article.exact_id"))
    exact_line_number = Column(Integer)
    exact_item_description = Column(String(255))
    exact_amount = Column(Numeric(precision=20, scale=3))
    exact_modified = Column(DateTime)

    article = relationship(Article, uselist=False)

    # Scheduled day
    scheduled_at = Column(DateTime, nullable=True)

    # Scheduled order of the day, 1 is first order of the day, 2 , 2nd etc.
    # No constraint for now, 2 lines scheduled the same day with the same priority
    # are ordered by the frontend
    schedule_priority = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    @property
    def gamme(self):
        if self.article and self.article.gamme:
            return self.article.gamme.exact_value
        return ""

    @property
    def item_code(self):
        if self.article:
            return self.article.exact_code

    def to_json(self):
        schema = OrderLineSchema()
        return schema.dump(self)
