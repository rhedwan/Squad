from rest_framework import generics
from .serializers import PaymentLinkSerializer
from .models import PaymentLink
from rest_framework.permissions import IsAuthenticated
import requests


class PaymentLinkCreateListView(generics.ListCreateAPIView):
    queryset = PaymentLink.objects.all()
    serializer_class = PaymentLinkSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InitiateTransaction(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        r = requests.post(
            "https://sandbox-api-d.squadco.com/transaction/initiate",
            data={
                "amount": 100,
                "email": "henimastic@gmail.com",
                "currency": "NGN",
                "initiate_type": "inline",
                "transaction_ref": "4678388588350909090AH",
                "callback_url": "http://squadco.com",
            },
        )
        return super().post(request, *args, **kwargs)
