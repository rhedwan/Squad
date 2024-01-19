from rest_framework import generics
from .serializers import TransactionSerializer, VirtualAccountSerializer
from .models import Transaction
from rest_framework.views import APIView
from rest_framework.response import Response
import hmac
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
import environ
import json
import requests
from urllib.parse import urljoin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

env = environ.Env()
environ.Env.read_env()

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = env("SECRET_KEY")


class TransactionView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class CreateVirtualAccountView(APIView):
    serializer_class = VirtualAccountSerializer

    @swagger_auto_schema(request_body=VirtualAccountSerializer)
    def post(self, request, format=None):
        serializer = VirtualAccountSerializer(data=request.data)
        if serializer.is_valid():
            BASE_URL = (
                "https://sandbox-api-d.squadco.com"  # e.g., "https://api.example.com"
            )

            # Prepare headers and data
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {SECRET_KEY}",
            }

            # Make the POST request
            response = requests.post(
                urljoin(BASE_URL, "/virtual-account"),
                headers=headers,
                json=serializer.data,
            )
            print(response.text)
            return Response(response.json(), status=200)  # or the API's response
        else:
            return Response(serializer.errors, status=400)


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
