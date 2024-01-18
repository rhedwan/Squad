from django.urls import path
from .views import PaymentLinkCreateListView

urlpatterns = [
    path(
        "paymentlink/", PaymentLinkCreateListView.as_view(), name="create_payment_link"
    )
]
