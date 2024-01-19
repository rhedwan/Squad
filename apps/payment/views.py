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
            body = payload.get("Body")

            transaction = Transaction(
                event=payload.get("Event"),
                transaction_ref=body.get("transaction_ref"),
                amount=body.get("amount"),
                gateway_ref=body.get("gateway_ref"),
                transaction_status=body.get("transaction_status"),
                email=body.get("email"),
                merchant_id=body.get("merchant_id"),
                currency=body.get("currency"),
                transaction_type=body.get("transaction_type"),
                merchant_amount=body.get("merchant_amount"),
                created_at=body.get("created_at"),
                payment_information=body.get("payment_information"),
                is_recurring=body.get("is_recurring"),
                meta=body.get("meta", {}),
            )
            transaction.save()

            # Now you can work with the payload dictionary
            # For example:

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
