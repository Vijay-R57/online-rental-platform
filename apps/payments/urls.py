from django.urls import path
from .views import (
    PaymentListView, CreatePaymentForLeaseView,
    SimulatedCheckoutView, PaymentReceiptView
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='list'),
    path('lease/<int:lease_id>/pay/', CreatePaymentForLeaseView.as_view(), name='create_for_lease'),
    path('<int:payment_id>/checkout/', SimulatedCheckoutView.as_view(), name='checkout'),
    path('<int:pk>/receipt/', PaymentReceiptView.as_view(), name='receipt'),
]
