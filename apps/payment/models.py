from django.db import models
import uuid
from django.contrib.auth import get_user_model

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


class PaymentLink(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_link_owner"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
