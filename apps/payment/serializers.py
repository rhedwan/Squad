from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class VirtualAccountSerializer(serializers.Serializer):
    customer_identifier = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    mobile_num = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    bvn = serializers.CharField(max_length=255)
    dob = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    address = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices=[("1", "Male"), ("2", "Female")])
    beneficiary_account = serializers.CharField(max_length=255)

    def validate(self, data):

        return data
