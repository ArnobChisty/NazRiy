from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .bkash_gateway import BkashGateway, BkashGatewayError, safe_provider_payload
from .models import Payment
from .sprint3_views import ProtectedView
from .sprint5_serializers import PaymentSerializer


class BkashGatewayConfigView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        automated = BkashGateway.configured()
        manual = bool(settings.BKASH_MERCHANT_NUMBER)
        response = Response({
            'mode': 'automated' if automated else ('manual' if manual else 'unavailable'),
            'automated': automated,
            'manual': manual,
            'merchant_number': settings.BKASH_MERCHANT_NUMBER if manual else '',
            'environment': settings.BKASH_GATEWAY_ENVIRONMENT if automated else '',
        })
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response


class BkashGatewayInitiateView(ProtectedView):
    @transaction.atomic
    def post(self, request, pk):
        payment = get_object_or_404(
            Payment.objects.select_for_update().select_related('order'),
            order_id=pk,
            order__user=request.user,
        )
        if payment.method != 'bkash':
            return Response({'detail': 'This order does not use bKash.'}, status=400)
        if payment.order.status == 'cancelled' or payment.status == 'cancelled':
            return Response({'detail': 'A cancelled order cannot be paid.'}, status=409)
        if payment.status == 'paid':
            return Response({'payment': PaymentSerializer(payment).data}, status=200)
        if payment.provider_payment_id and payment.provider_redirect_url:
            return Response({
                'payment': PaymentSerializer(payment).data,
                'redirect_url': payment.provider_redirect_url,
            })

        try:
            gateway = BkashGateway()
            callback_url = settings.BKASH_GATEWAY_CALLBACK_URL or request.build_absolute_uri(
                reverse('bkash-gateway-callback')
            )
            invoice = f'NR-{payment.order_id}-{payment.idempotency_key.hex[:8]}-{payment.attempts + 1}'
            provider = gateway.create_payment(
                amount=payment.amount,
                invoice=invoice,
                payer_reference=str(request.user.pk),
                callback_url=callback_url,
            )
        except BkashGatewayError as error:
            payment.failure_reason = str(error)
            payment.save(update_fields=['failure_reason', 'updated_at'])
            return Response({'detail': str(error)}, status=status.HTTP_502_BAD_GATEWAY)

        payment_id = str(provider.get('paymentID', ''))
        redirect_url = str(provider.get('bkashURL', ''))
        if str(provider.get('statusCode', '')) != '0000' or not payment_id or not redirect_url:
            reason = provider.get('statusMessage') or 'bKash could not create the payment.'
            payment.failure_reason = reason
            payment.provider_payload = safe_provider_payload(provider)
            payment.save(update_fields=['failure_reason', 'provider_payload', 'updated_at'])
            return Response({'detail': reason}, status=status.HTTP_502_BAD_GATEWAY)

        payment.provider_payment_id = payment_id
        payment.provider_invoice = invoice
        payment.provider_redirect_url = redirect_url
        payment.provider_payload = safe_provider_payload(provider)
        payment.failure_reason = ''
        payment.status = 'pending'
        payment.attempts += 1
        payment.save()
        return Response({
            'payment': PaymentSerializer(payment).data,
            'redirect_url': redirect_url,
        }, status=status.HTTP_201_CREATED)


class BkashGatewayCallbackView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def _redirect(self, payment, result):
        query = urlencode({'payment': result})
        return HttpResponseRedirect(f"{settings.FRONTEND_URL.rstrip('/')}/orders/{payment.order_id}?{query}")

    def get(self, request):
        payment_id = request.query_params.get('paymentID', '').strip()
        callback_status = request.query_params.get('status', '').strip().lower()
        payment = get_object_or_404(Payment.objects.select_related('order'), provider_payment_id=payment_id)
        if payment.status == 'paid':
            return self._redirect(payment, 'success')

        if callback_status != 'success':
            with transaction.atomic():
                locked = Payment.objects.select_for_update().get(pk=payment.pk)
                if locked.status != 'paid':
                    locked.status = 'failed'
                    locked.failure_reason = 'The customer cancelled bKash checkout.' if callback_status == 'cancel' else 'bKash checkout was not completed.'
                    locked.provider_payment_id = ''
                    locked.provider_redirect_url = ''
                    locked.save()
            return self._redirect(payment, 'cancelled' if callback_status == 'cancel' else 'failed')

        try:
            provider = BkashGateway().verify_completed_payment(payment_id)
            provider_amount = Decimal(str(provider.get('amount')))
        except (BkashGatewayError, InvalidOperation, TypeError) as error:
            reason = str(error) if str(error) else 'bKash payment verification failed.'
            with transaction.atomic():
                locked = Payment.objects.select_for_update().get(pk=payment.pk)
                if locked.status != 'paid':
                    locked.status = 'failed'
                    locked.failure_reason = reason
                    locked.provider_payload = safe_provider_payload(provider) if 'provider' in locals() else {}
                    locked.provider_payment_id = ''
                    locked.provider_redirect_url = ''
                    locked.save()
            return self._redirect(payment, 'failed')

        provider_invoice = str(provider.get('merchantInvoiceNumber', ''))
        if provider_amount != payment.amount or (provider_invoice and provider_invoice != payment.provider_invoice):
            with transaction.atomic():
                locked = Payment.objects.select_for_update().get(pk=payment.pk)
                locked.status = 'failed'
                locked.failure_reason = 'bKash returned payment details that do not match this order.'
                locked.provider_payload = safe_provider_payload(provider)
                locked.save()
            return self._redirect(payment, 'failed')

        with transaction.atomic():
            locked = Payment.objects.select_for_update().select_related('order').get(pk=payment.pk)
            if locked.order.status == 'cancelled':
                locked.status = 'failed'
                locked.failure_reason = 'The order was cancelled before payment confirmation.'
            else:
                locked.status = 'paid'
                locked.provider_reference = str(provider.get('trxID', ''))
                locked.failure_reason = ''
            locked.provider_payload = safe_provider_payload(provider)
            locked.provider_redirect_url = ''
            locked.save()
        return self._redirect(locked, 'success' if locked.status == 'paid' else 'failed')
