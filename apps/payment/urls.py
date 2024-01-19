from django.urls import path
from .views import TransactionView, webhook_endpoint, CreateVirtualAccountView


urlpatterns = [
    path("view_all_payment/", TransactionView.as_view(), name="view_payment"),
    path("webhook-url/", webhook_endpoint, name="webhook_endpoint"),
    path(
        "create-virtual-account/",
        CreateVirtualAccountView.as_view(),
        name="create_virtual_account",
    ),
]
