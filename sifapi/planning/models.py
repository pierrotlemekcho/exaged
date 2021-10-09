from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = "alembic_version"


class Article(models.Model):
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    exact_code = models.CharField(max_length=255, blank=True, null=True)
    exact_description = models.CharField(max_length=255, blank=True, null=True)
    exact_modified = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "article"


class Commande(models.Model):
    exact_order_id = models.CharField(
        unique=True, max_length=255, blank=True, null=True
    )
    exact_tier = models.ForeignKey(
        "Tier", models.CASCADE, blank=True, null=True, to_field="exact_id"
    )
    exact_order_description = models.CharField(max_length=255, blank=True, null=True)
    exact_your_ref = models.CharField(max_length=255, blank=True, null=True)
    exact_order_number = models.IntegerField(blank=True, null=True)
    exact_status = models.IntegerField(blank=True, null=True)
    exact_status_description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    exact_amount = models.DecimalField(
        max_digits=20, decimal_places=3, blank=True, null=True
    )
    exact_modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "commande"


class Devis(models.Model):
    exact_quotation_id = models.CharField(
        unique=True, max_length=255, blank=True, null=True
    )
    exact_quotation_number = models.IntegerField(blank=True, null=True)
    exact_tier = models.ForeignKey(
        "Tier", models.CASCADE, blank=True, null=True, to_field="exact_id"
    )
    exact_your_ref = models.CharField(max_length=255, blank=True, null=True)
    exact_order_description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "devis"


class Gamme(models.Model):
    exact_item = models.ForeignKey(
        Article, on_delete=models.CASCADE, blank=True, null=True, to_field="exact_id"
    )
    exact_value = models.CharField(max_length=255, blank=True, null=True)
    exact_modified = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gamme"


class LastSyncSuccess(models.Model):
    sync_type = models.CharField(primary_key=True, max_length=255)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "last_sync_success"


class LigneDeCommande(models.Model):
    exact_order = models.ForeignKey(
        Commande, models.CASCADE, blank=True, null=True, to_field="exact_order_id"
    )
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    exact_item = models.ForeignKey(
        Article, models.CASCADE, blank=True, null=True, to_field="exact_id"
    )
    exact_line_number = models.IntegerField(blank=True, null=True)
    exact_item_description = models.CharField(max_length=255, blank=True, null=True)
    exact_amount = models.DecimalField(
        max_digits=20, decimal_places=3, blank=True, null=True
    )
    exact_modified = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Scheduled order of the day, 1 is first order of the day, 2 , 2nd etc.
    # No constraint for now, 2 lines scheduled the same day with the same priority
    # are ordered by the frontend
    schedule_priority = models.IntegerField(default=1)
    scheduled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "ligne_de_commande"


class Tier(models.Model):
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    exact_account_code = models.CharField(max_length=255, blank=True, null=True)
    exact_name = models.CharField(max_length=255, blank=True, null=True)
    exact_is_supplier = models.IntegerField(blank=True, null=True)
    exact_is_reseller = models.IntegerField(blank=True, null=True)
    exact_is_sales = models.IntegerField(blank=True, null=True)
    exact_is_purchase = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tier"


class TierClient(models.Model):
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    prefixed_account_code = models.CharField(max_length=255, blank=True, null=True)
    exact_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tier_client"


class TierSupplier(models.Model):
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    prefixed_account_code = models.CharField(max_length=255, blank=True, null=True)
    exact_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tier_supplier"


class WebCam(models.Model):
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
