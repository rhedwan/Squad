from django.db import models
import uuid
from django.contrib.auth import get_user_model
import json

User = get_user_model()


# Create your models here.
class TimeStampedModel(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]


class Transaction(models.Model):
    event = models.CharField(max_length=255)
    transaction_ref = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()
    gateway_ref = models.CharField(max_length=255)
    transaction_status = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    merchant_id = models.CharField(max_length=255)
    currency = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=50)
    merchant_amount = models.IntegerField()
    created_at = models.DateTimeField()
    payment_information = models.JSONField()  # Requires Django 3.1+
    is_recurring = models.BooleanField()

    # The 'meta' field is nested in the JSON. It's stored here as a JSONField.
    meta = models.JSONField()

    def set_meta(self, meta):
        self.meta = json.dumps(meta)

    def get_meta(self):
        return json.loads(self.meta)
