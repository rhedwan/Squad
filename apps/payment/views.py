from rest_framework import generics
from .serializers import PaymentLinkSerializer
from .models import PaymentLink
from rest_framework.permissions import IsAuthenticated
import requests

# views.py within your Django app

import hmac
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
import environ
import json

env = environ.Env()
environ.Env.read_env()

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = env("SECRET_KEY")


@require_POST
@csrf_exempt
def webhook_endpoint(request):
    try:
        raw_body = request.body.decode("utf-8")  # Decode the bytes to string
        request_body = force_bytes(raw_body)
        received_signature = request.headers.get("x-squad-encrypted-body", "")
        expected_signature = (
            hmac.new(
                force_bytes(SECRET_KEY), msg=request_body, digestmod=hashlib.sha512
            )
            .hexdigest()
            .upper()
        )

        if received_signature == expected_signature:
            # Signature matches, you can trust the event came from Squad
            payload = json.loads(raw_body)  # Here you parse the JSON payload
            print(payload)

            # Now you can work with the payload dictionary
            # For example:
            event_type = payload.get("event_type")  # Access data from the payload
            print(event_type)

            # ... (The rest of your event processing logic goes here)

            # After processing the event...
            return JsonResponse({"status": "success"}, status=200)

        else:
            # The request didn't come from Squad, ignore it
            return JsonResponse({"status": "invalid_signature"}, status=400)

    except json.JSONDecodeError as e:
        # In case JSON is not properly formatted
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        # Handle other unexpected errors
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


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
