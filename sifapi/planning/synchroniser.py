import datetime

from exactonline.resource import GET
from pytz import timezone

from planning.models import (Article, Commande, Devis, Gamme, LigneDeCommande,
                             Tier, TierClient, TierSupplier)
from planning.util import parse_exact_api_date

EXACT_STATUS_OPEN = 12
EXACT_STATUS_PARTIAL = 20


class Synchronizer:
    def __init__(self, api, division, since):
        self.api = api
        self.division = division
        if not since:
            since = datetime.datetime.fromtimestamp(0)
        self.since = since
        # Date filter with exact online are in Amsterdam time (CET or CEST)
        amsterdam = timezone("Europe/Amsterdam")
        self.since_string = since.astimezone(amsterdam).replace(tzinfo=None).isoformat()

    def _build_tier_detail(self, clazz, tier, prefix):
        tier_detail = clazz.objects.filter(exact_id=tier.exact_id).first()
        if not tier_detail:
            tier_detail = clazz(exact_id=tier.exact_id)
        tier_detail.prefixed_account_code = f"{prefix}{tier.exact_account_code.strip()}"
        tier_detail.exact_name = tier.exact_name
        return tier_detail

    def _build_tier(self, exact_tier):
        tier = Tier.objects.filter(exact_id=exact_tier["ID"]).first()
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
            tier.save()
            # Clients
            if tier.exact_is_sales:
                tier_client = self._build_tier_detail(TierClient, tier, "c_")
                tier_client.save()
            # Fournisseurs
            if tier.exact_is_supplier is True:
                tier_supplier = self._build_tier_detail(TierSupplier, tier, "f_")
                tier_supplier.save()

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
            quote = Devis.objects.filter(
                exact_quotation_id=exact_devis["QuotationID"]
            ).first()
            tier = Tier.objects.filter(exact_id=exact_devis["OrderAccount"]).first()
            if not quote:
                quote = Devis(exact_quotation_id=exact_devis["QuotationID"])
            quote.exact_quotation_number = exact_devis["QuotationNumber"]
            quote.exact_order_description = exact_devis["Description"]
            quote.exact_tier = tier
            quote.exact_your_ref = exact_devis["YourRef"]
            quote.save()
            counter = counter + 1
        return counter

    def synchronize_gammes(self):
        gammes = self.api.restv1(
            GET(
                f"read/logistics/ItemExtraField?$filter=Description+eq+'gamme'+and+Modified+gt+DateTime'{self.since_string}'"
            )
        )
        for exact_gamme in gammes:
            gamme = Gamme.objects.filter(
                exact_item__exact_id=exact_gamme["ItemID"]
            ).first()
            if not gamme:
                gamme = Gamme(exact_item_id=exact_gamme["ItemID"])
            gamme.exact_value = exact_gamme["Value"]
            gamme.exact_modified = parse_exact_api_date(exact_gamme["Modified"])
            gamme.save()
        return len(gammes)

    def synchronize_articles(self):
        articles = self.api.restv1(
            GET(
                f"logistics/Items?$select=ID,Code,Description,Modified&$filter=Modified+gt+DateTime'{self.since_string}'"
            )
        )

        for exact_article in articles:
            article = Article.objects.filter(exact_id=exact_article["ID"]).first()
            if not article:
                article = Article(exact_id=exact_article["ID"])
            article.exact_code = exact_article["Code"]
            article.exact_description = exact_article["Description"]
            article.exact_modified = parse_exact_api_date(exact_article["Modified"])
            article.save()
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
            commande = Commande.objects.filter(
                exact_order_id=exact_order["OrderID"]
            ).first()
            tier = Tier.objects.filter(exact_id=exact_order["OrderedBy"]).first()
            if not commande:
                commande = Commande(exact_order_id=exact_order["OrderID"])
            commande.exact_tier = tier
            commande.exact_order_description = exact_order["Description"]
            commande.exact_your_ref = exact_order["YourRef"]
            commande.exact_order_number = exact_order["OrderNumber"]
            commande.exact_status_description = exact_order["StatusDescription"]
            commande.exact_status = exact_order["Status"]
            commande.exact_modified = parse_exact_api_date(exact_order["Modified"])
            commande.save()

            exact_lines = exact_order["SalesOrderLines"]["results"]
            # delete lines that are not in exact anymore
            all_exact_line_ids = [exact_line["ID"] for exact_line in exact_lines]

            for line in commande.lines.all():
                if line.exact_id not in all_exact_line_ids:
                    line.delete()

            for exact_line in exact_lines:
                line = LigneDeCommande.objects.filter(exact_id=exact_line["ID"]).first()
                if not line:
                    line = LigneDeCommande(exact_id=exact_line["ID"])
                line.exact_item_id = exact_line["Item"]
                line.exact_line_number = exact_line["LineNumber"]
                line.exact_item_description = exact_line["ItemDescription"]
                line.exact_notes = exact_line["Notes"]
                line.exact_amount = exact_line["AmountDC"]
                line.exact_order = commande
                line.save()
            counter = counter + 1
        return counter

    ## Look for all open or partial orders that are still in our db but not in exact and delete them
    def synchronize_deleted_commandes(self):
        counter = 0
        partial_or_open_exact_commandes = self.api.restv1(
            GET(
                f"salesorder/SalesOrders?$select=OrderID,Status&$filter=Status+eq+{EXACT_STATUS_PARTIAL}+or+Status+eq+{EXACT_STATUS_OPEN}"
            )
        )

        exact_commandes_id = [
            commande["OrderID"] for commande in partial_or_open_exact_commandes
        ]

        commandes = Commande.objects.filter(
            exact_status__in=[EXACT_STATUS_PARTIAL, EXACT_STATUS_OPEN]
        )

        for commande in commandes:
            if commande.exact_order_id not in exact_commandes_id:
                commande.delete()
                counter = counter + 1
        return counter
