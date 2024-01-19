from django.urls import path
from .views import PaymentLinkCreateListView, webhook_endpoint


urlpatterns = [
    path(
        "paymentlink/", PaymentLinkCreateListView.as_view(), name="create_payment_link"
    ),
    path("webhook-url/", webhook_endpoint, name="webhook_endpoint"),
]
