import json
import re

from django.conf import settings
from django.db import models
from django.utils.html import format_html


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

    @property
    def folder_path(self):
        return f"{settings.SHARE_ORDER_FOLDER}{self.exact_tier.exact_name}/C{self.exact_order_number}/"


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
        Article,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        to_field="exact_id",
        related_name="gamme",
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
    PARTS_ON_SITE = "sur_place"
    PARTS_PARTIAL = "partiel"
    PARTS_UNAVAILABLE = "non_dispo"

    PARTS_STATUS_CHOICES = [
        (PARTS_ON_SITE, "Sur Place"),
        (PARTS_PARTIAL, "Partiel"),
        (PARTS_UNAVAILABLE, "Non Dispo"),
    ]

    exact_order = models.ForeignKey(
        Commande,
        models.CASCADE,
        blank=True,
        null=True,
        to_field="exact_order_id",
        related_name="lines",
    )
    exact_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    exact_item = models.ForeignKey(
        Article, models.CASCADE, blank=True, null=True, to_field="exact_id"
    )
    exact_line_number = models.IntegerField(blank=True, null=True)
    exact_item_description = models.CharField(max_length=255, blank=True, null=True)
    exact_notes = models.CharField(max_length=255, blank=True, null=True)
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
    # To keep track if the gamme operations have been performed
    gamme_status = models.TextField(blank=True)
    # Are the parts on site or no
    parts_status = models.CharField(
        max_length=10, choices=PARTS_STATUS_CHOICES, default=PARTS_UNAVAILABLE
    )
    comments = models.TextField(blank=True)

    class Meta:
        db_table = "ligne_de_commande"

    @property
    def item_code(self):
        if self.exact_item:
            return self.exact_item.exact_code

    @property
    def gamme(self):
        if self.exact_item and self.exact_item.gamme.first():
            return self.exact_item.gamme.first().exact_value
        return ""

    @property
    def gamme_list(self):
        return re.findall(r"((?:[^_\*\$#]+)|(?:#|\$|\*){1})", self.gamme)


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
    hex_color = models.CharField(max_length=7, null=True)

    # Color span used in the admin interface
    @property
    def color_span(self):
        if self.hex_color:
            return format_html(
                '<span style="background-color: {};">&nbsp;&nbsp;&nbsp</span>',
                self.hex_color,
            )

    def __str__(self):
        return f"{self.exact_name}"

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


class Operation(models.Model):
    code = models.CharField(max_length=255)
    hex_color = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.code}"

    @property
    def color_span(self):
        if self.hex_color:
            return format_html(
                '<span style="background-color: {};">&nbsp;&nbsp;&nbsp</span>',
                self.hex_color,
            )
