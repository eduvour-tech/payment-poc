# core/views.py

import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from razorpay.errors import SignatureVerificationError
import hmac
import hashlib
# core/views.py
from django.shortcuts import render

def razorpay_test_page(request):
    return render(request, "pay.html")

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderAPIView(APIView):
    def post(self, request):
        amount = request.data.get('amount')  # amount in rupees
        amount_paise = int(amount) * 100

        data = {
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": "1"
        }

        order = client.order.create(data=data)
        
        # save to DB (optional)
        Payment.objects.create(order_id=order['id'], amount=amount)

        return Response({
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

class VerifyPaymentAPIView(APIView):
    def post(self, request):
        data = request.data

        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        try:
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()

            if generated_signature != razorpay_signature:
                return Response({"error": "Signature verification failed"}, status=400)

            # mark payment as done
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.is_paid = True
            payment.payment_id = razorpay_payment_id
            payment.save()

            return Response({"message": "Payment successful"})
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)