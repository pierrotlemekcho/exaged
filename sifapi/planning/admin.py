from django.contrib import admin

from .models import (Article, Commande, Devis, Gamme, LastSyncSuccess,
                     LigneDeCommande, Operation, Tier, TierClient,
                     TierSupplier, WebCam)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    pass


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    pass


@admin.register(Gamme)
class GammeAdmin(admin.ModelAdmin):
    pass


@admin.register(LastSyncSuccess)
class LastSyncSuccessAdmin(admin.ModelAdmin):
    pass


@admin.register(LigneDeCommande)
class LigneDeCommandeAdmin(admin.ModelAdmin):
    pass


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ["id", "exact_name", "exact_account_code", "hex_color", "color_span"]
    list_filter = ["exact_name"]
    pass


@admin.register(WebCam)
class WebCamAdmin(admin.ModelAdmin):
    pass


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    pass
