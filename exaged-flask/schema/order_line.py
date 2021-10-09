from marshmallow import EXCLUDE, Schema, fields


class OrderLineSchema(Schema):
    exact_id = fields.String()
    scheduled_at = fields.DateTime()
    schedule_priority = fields.Integer()
    item_code = fields.String()
    gamme = fields.String()
    exact_order_id = fields.String()
    exact_line_number = fields.Integer()
    exact_amount = fields.Number()

    class Meta:
        unknown = EXCLUDE
