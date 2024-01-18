from rest_framework import serializers
from .models import PaymentLink


class PaymentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLink
        fields = [
            "pkid",
            "id",
            "created_at",
            "updated_at",
            "name",
            "description",
            "price",
            # "created_by",
        ]
