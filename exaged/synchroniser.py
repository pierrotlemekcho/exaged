from exaged.model.tier import Tier
from exaged.model.devis import Devis
from exaged.model.commande import Commande
from exactonline.resource import GET


class Synchronizer:
    def __init__(self, db, api, division):
        self.db = db
        self.api = api
        self.division = division

    def synchonize_tiers(self):
        counter=0;
        tiers = self.api.relations.filter(
            select='ID,Code,Name,IsSales,IsSupplier,IsReseller,IsSales,IsPurchase')
        for exact_tier in tiers:
            tier = self.db.query(Tier).filter_by(exact_id=exact_tier['ID']).first()
            if not tier:
                tier = Tier(exact_id=exact_tier['ID'])
            tier.exact_account_code = exact_tier['Code']
            tier.exact_name = exact_tier['Name']
            tier.exact_is_supplier = exact_tier['IsSupplier']
            tier.exact_is_reseller = exact_tier['IsReseller']
            tier.exact_is_sales = exact_tier['IsSales']
            tier.exact_is_purchase = exact_tier['IsPurchase']
            self.db.add(tier)
            counter = counter+1
        return counter


    def synchronize_devis(self):
        counter=0;
        devis = self.api.restv1(GET('crm/Quotations?$select=QuotationID,OrderAccount,QuotationNumber,YourRef,Description'))

        for exact_devis in devis:
            quote = self.db.query(Devis).filter_by(
                exact_quotation_id=exact_devis['QuotationID']).first()
            tier = self.db.query(Tier).filter_by(
                exact_id=exact_devis['OrderAccount']).first()
            if not quote:
                quote = Devis(exact_quotation_id=exact_devis['QuotationID'])
            quote.exact_quotation_number = exact_devis['QuotationNumber']
            quote.exact_order_description = exact_devis['Description']
            quote.tier = tier
            quote.exact_your_ref = exact_devis['YourRef']
            self.db.add(quote)
            counter = counter+1
        return counter

    def synchronize_commandes(self):
        counter=0
        commandes = self.api.restv1(GET('salesorder/SalesOrders?$select=OrderID,Description,OrderedBy,YourRef,OrderNumber'))

        for exact_order in commandes:
            commande = self.db.query(Commande).filter_by(
                exact_order_id=exact_order['OrderID']).first()
            tier = self.db.query(Tier).filter_by(
                exact_id=exact_order['OrderedBy']).first()
            if not commande:
                commande = Commande(exact_order_id=exact_order['OrderID'])
            commande.tier = tier
            commande.exact_order_description = exact_order['Description']
            commande.exact_your_ref = exact_order['YourRef']
            commande.exact_order_number = exact_order['OrderNumber']

            self.db.add(commande)
            counter = counter+1
        return counter
