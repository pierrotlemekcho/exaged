from rest_framework import serializers

from planning.models import Commande, LigneDeCommande, Operation, Tier, WebCam


class WebCamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebCam
        fields = ["name", "id"]


class TierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "exact_id", "exact_name", "hex_color"]


class OperationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Operation
        fields = ["id", "hex_color", "code"]


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
            "gamme_status",
            "gamme_list",
            "exact_order_id",
            "exact_line_number",
            "exact_amount",
            "parts_status",
            "comments",
        ]
        read_only_fields = ["gamme", "gamme_list", "item_code"]


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
            "exact_your_ref",
            "exact_tier_id",
            "exact_status",
            "lines",
            "exact_tier",
        ]
