from rest_framework import serializers

from planning.models import Commande, LigneDeCommande, Tier, WebCam


class WebCamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebCam
        fields = ["name", "id"]


class TierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "exact_id", "exact_name"]


class OrderLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LigneDeCommande
        fields = [
            "id",
            "exact_id",
            "scheduled_at",
            "schedule_priority",
            "item_code",
            "gamme",
            "exact_order_id",
            "exact_line_number",
            "exact_amount",
        ]


class CommandeSerializer(serializers.HyperlinkedModelSerializer):
    lines = OrderLineSerializer(many=True)
    exact_tier = TierSerializer()

    class Meta:
        model = Commande
        fields = [
            "id",
            "exact_order_id",
            "exact_order_number",
            "exact_order_description",
            "exact_tier_id",
            "exact_status",
            "lines",
            "exact_tier",
        ]
