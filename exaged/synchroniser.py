import datetime

from exactonline.resource import GET
from pytz import timezone, utc

from exaged.model.article import Article
from exaged.model.commande import Commande
from exaged.model.devis import Devis
from exaged.model.gamme import Gamme
from exaged.model.ligne_de_commande import LigneDeCommande
from exaged.model.tier import Tier
from exaged.model.tier_client import TierClient
from exaged.model.tier_supplier import TierSupplier
from exaged.util import parse_exact_api_date


class Synchronizer:
    def __init__(self, db, api, division, since):
        self.db = db
        self.api = api
        self.division = division
        if not since:
            since = datetime.datetime.fromtimestamp(0)
        self.since = since
        # Date filter with exact online are in Amsterdam time (CET or CEST)
        amsterdam = timezone("Europe/Amsterdam")
        self.since_string = (
            utc.localize(since).astimezone(amsterdam).replace(tzinfo=None).isoformat()
        )

    def _build_tier_detail(self, clazz, tier, prefix):
        tier_detail = self.db.query(clazz).filter_by(exact_id=tier.exact_id).first()
        if not tier_detail:
            tier_detail = clazz(exact_id=tier.exact_id)
        tier_detail.prefixed_account_code = f"{prefix}{tier.exact_account_code.strip()}"
        tier_detail.exact_name = tier.exact_name
        return tier_detail

    def _build_tier(self, exact_tier):
        tier = self.db.query(Tier).filter_by(exact_id=exact_tier["ID"]).first()
        if not tier:
            tier = Tier(exact_id=exact_tier["ID"])
        tier.exact_account_code = exact_tier["Code"]
        tier.exact_name = exact_tier["Name"]
        tier.exact_is_supplier = exact_tier["IsSupplier"]
        tier.exact_is_reseller = exact_tier["IsReseller"]
        tier.exact_is_sales = exact_tier["IsSales"]
        tier.exact_is_purchase = exact_tier["IsPurchase"]
        return tier

    def synchronize_tiers(self):
        counter = 0
        tiers = self.api.relations.filter(
            select="ID,Code,Name,IsSales,IsSupplier,IsReseller,IsSales,IsPurchase",
            filter=f"Modified gt DateTime'{self.since_string}'",
        )
        for exact_tier in tiers:
            tier = self._build_tier(exact_tier)
            self.db.add(tier)
            # Clients
            if tier.exact_is_sales:
                tier_client = self._build_tier_detail(TierClient, tier, "c_")
                self.db.add(tier_client)
            # Fournisseurs
            if tier.exact_is_supplier is True:
                tier_supplier = self._build_tier_detail(TierSupplier, tier, "f_")
                self.db.add(tier_supplier)

            counter = counter + 1
        return counter

    def synchronize_devis(self):
        counter = 0
        devis = self.api.restv1(
            GET(
                f"crm/Quotations?$select=QuotationID,OrderAccount,QuotationNumber,YourRef,Description&$filter=Modified+gt+DateTime'{self.since_string}'"
            )
        )

        for exact_devis in devis:
            quote = (
                self.db.query(Devis)
                .filter_by(exact_quotation_id=exact_devis["QuotationID"])
                .first()
            )
            tier = (
                self.db.query(Tier)
                .filter_by(exact_id=exact_devis["OrderAccount"])
                .first()
            )
            if not quote:
                quote = Devis(exact_quotation_id=exact_devis["QuotationID"])
            quote.exact_quotation_number = exact_devis["QuotationNumber"]
            quote.exact_order_description = exact_devis["Description"]
            quote.tier = tier
            quote.exact_your_ref = exact_devis["YourRef"]
            self.db.add(quote)
            counter = counter + 1
        return counter

    def synchronize_gammes(self):
        gammes = self.api.restv1(
            GET(
                f"read/logistics/ItemExtraField?$filter=Description+eq+'gamme'+and+Modified+gt+DateTime'{self.since_string}'"
            )
        )
        for exact_gamme in gammes:
            gamme = (
                self.db.query(Gamme)
                .filter_by(exact_item_id=exact_gamme["ItemID"])
                .first()
            )
            if not gamme:
                gamme = Gamme(exact_item_id=exact_gamme["ItemID"])
            gamme.exact_value = exact_gamme["Value"]
            gamme.exact_modified = parse_exact_api_date(exact_gamme["Modified"])
            self.db.add(gamme)
        return len(gammes)

    def synchronize_articles(self):
        articles = self.api.restv1(
            GET(
                f"logistics/Items?$select=ID,Code,Description,Modified&$filter=Modified+gt+DateTime'{self.since_string}'"
            )
        )

        for exact_article in articles:
            article = (
                self.db.query(Article).filter_by(exact_id=exact_article["ID"]).first()
            )
            if not article:
                article = Article(exact_id=exact_article["ID"])
            article.exact_code = exact_article["Code"]
            article.exact_description = exact_article["Description"]
            article.exact_modified = parse_exact_api_date(exact_article["Modified"])
            self.db.add(article)
        return len(articles)

    def synchronize_commandes(self):
        counter = 0
        # fifteen_days_ago = datetime.datetime.now() - datetime.timedelta(15)
        # commandes = self.api.restv1(GET(f"salesorder/SalesOrders?$select=SalesOrderLines,OrderID,Description,OrderedBy,YourRef,OrderNumber,Status,StatusDescription,Modified&$expand=SalesOrderLines&$filter=Modified+gt+DateTime'{fifteen_days_ago.isoformat()}'"))
        commandes = self.api.restv1(
            GET(
                f"salesorder/SalesOrders?$select=SalesOrderLines,OrderID,Description,OrderedBy,YourRef,OrderNumber,Status,StatusDescription,Modified,SalesOrderLines&$expand=SalesOrderLines&$filter=Modified+gt+DateTime'{self.since_string}'"
            )
        )

        for exact_order in commandes:
            commande = (
                self.db.query(Commande)
                .filter_by(exact_order_id=exact_order["OrderID"])
                .first()
            )
            tier = (
                self.db.query(Tier).filter_by(exact_id=exact_order["OrderedBy"]).first()
            )
            if not commande:
                commande = Commande(exact_order_id=exact_order["OrderID"])
            commande.tier = tier
            commande.exact_order_description = exact_order["Description"]
            commande.exact_your_ref = exact_order["YourRef"]
            commande.exact_order_number = exact_order["OrderNumber"]
            commande.exact_status_description = exact_order["StatusDescription"]
            commande.exact_status = exact_order["Status"]
            commande.exact_modified = parse_exact_api_date(exact_order["Modified"])

            exact_lines = exact_order["SalesOrderLines"]["results"]
            commande_lignes = []
            for exact_line in exact_lines:
                line = (
                    self.db.query(LigneDeCommande)
                    .filter_by(exact_id=exact_line["ID"])
                    .first()
                )
                if not line:
                    line = LigneDeCommande(exact_id=exact_line["ID"])
                line.exact_item_id = exact_line["Item"]
                line.exact_line_number = exact_line["LineNumber"]
                line.exact_item_description = exact_line["ItemDescription"]
                line.exact_amount = exact_line["AmountDC"]
                commande_lignes.append(line)
            commande.lignes = commande_lignes

            self.db.add(commande)
            counter = counter + 1
        return counter
