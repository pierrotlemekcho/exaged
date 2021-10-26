from rest_framework import serializers

from planning.models import Commande, LigneDeCommande, Operation, Tier, WebCam


class WebCamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebCam
        fields = ["name", "id"]
        read_only_fields = ["name", "id"]


class TierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "exact_id", "exact_name", "hex_color"]
        read_only_fields = ["id", "exact_id", "exact_name", "hex_color"]


class OperationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Operation
        fields = ["id", "hex_color", "code"]
        read_only_fields = ["id", "hex_color", "code"]


# Not logged in users can only change the parts_status
class AnonymousOrderLineSerializer(serializers.HyperlinkedModelSerializer):
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
            "parts_status",
            "comments",
        ]
        read_only_fields = [
            "gamme",
            "item_code",
            "exact_line_number",
            "gamme_list",
            "item_code",
            "scheduled_at",
            "schedule_priority",
            "comments",
        ]


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


# Anonymous request don't get all the info
class AnonymousCommandeSerializer(serializers.HyperlinkedModelSerializer):
    lines = AnonymousOrderLineSerializer(many=True, read_only=True)
    exact_tier = TierSerializer(read_only=True)

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
