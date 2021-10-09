from rest_framework import serializers

from planning.models import Commande, Tier, WebCam


class WebCamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebCam
        fields = ["name", "id"]


class TierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "exact_id", "exact_name"]


class CommandeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Commande
        fields = [
            "id",
            "exact_order_id",
            "exact_order_number",
            "exact_order_description",
            "exact_tier_id",
            "exact_status",
        ]
