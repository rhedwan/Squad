from django.urls import path
from .views import TransactionView, webhook_endpoint


urlpatterns = [
    path("view_all_payment/", TransactionView.as_view(), name="view_payment"),
    path("webhook-url/", webhook_endpoint, name="webhook_endpoint"),
]
