# core/urls.py

from django.urls import path
from .views import CreateOrderAPIView, VerifyPaymentAPIView, razorpay_test_page

urlpatterns = [
    path('create-order/', CreateOrderAPIView.as_view(), name='create-order'),
    path('verify-payment/', VerifyPaymentAPIView.as_view(), name='verify-payment'),
    path('pay-test/', razorpay_test_page, name='pay-test'),
]
