from rest_framework import generics
from .serializers import TransactionSerializer
from .models import Transaction

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


class TransactionView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


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
            # print(payload)
            transaction = Transaction(
                event=payload.get("Event"),
                transaction_ref=payload.get("transaction_ref"),
                amount=payload.get("amount"),
                gateway_ref=payload.get("gateway_ref"),
                transaction_status=payload.get("transaction_status"),
                email=payload.get("email"),
                merchant_id=payload.get("merchant_id"),
                currency=payload.get("currency"),
                transaction_type=payload.get("transaction_type"),
                merchant_amount=payload.get("merchant_amount"),
                created_at=payload.get("created_at"),
                payment_information=payload.get("payment_information"),
                is_recurring=payload.get("is_recurring"),
                meta=payload.get("meta", {}),
            )
            transaction.save()

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
