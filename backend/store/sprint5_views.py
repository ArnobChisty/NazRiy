from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import Payment
from .sprint3_views import ProtectedView
from .sprint5_serializers import PaymentActionSerializer, PaymentSerializer


class BkashPaymentView(ProtectedView):
    """Accept a customer-supplied bKash TrxID for administrator verification."""

    @transaction.atomic
    def post(self, request, pk):
        payment = get_object_or_404(
            Payment.objects.select_for_update().select_related('order'),
            order_id=pk,
            order__user=request.user,
        )
        serializer = PaymentActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        request_id = data['request_id']

        if payment.last_request_id == request_id:
            return Response(PaymentSerializer(payment).data)

        if data['action'] == 'cancel':
            if payment.status == 'paid':
                return Response({'detail': 'A verified payment cannot be cancelled.'}, status=409)
            if payment.status != 'cancelled':
                payment.status = 'cancelled'
                payment.failure_reason = 'Cancelled by the customer before bKash verification.'
                payment.last_request_id = request_id
                payment.save()
                if payment.order.status != 'cancelled':
                    payment.order.status = 'cancelled'
                    payment.order.save()
            return Response(PaymentSerializer(payment).data)

        if payment.method != 'bkash':
            return Response(
                {'detail': 'Cash-on-delivery orders do not require a bKash transaction ID.'},
                status=400,
            )
        if payment.status == 'cancelled':
            return Response({'detail': 'A cancelled payment cannot be submitted.'}, status=409)
        if payment.status == 'paid':
            return Response(PaymentSerializer(payment).data)

        transaction_id = data['transaction_id'].upper()
        duplicate = Payment.objects.exclude(pk=payment.pk).filter(
            method='bkash',
            provider_reference__iexact=transaction_id,
        ).exists()
        if duplicate:
            return Response(
                {'detail': 'This bKash transaction ID has already been used.'},
                status=status.HTTP_409_CONFLICT,
            )

        payment.attempts += 1
        payment.last_request_id = request_id
        payment.provider_reference = transaction_id
        payment.status = 'pending'
        payment.failure_reason = ''
        try:
            with transaction.atomic():
                payment.save()
        except IntegrityError:
            return Response(
                {'detail': 'This bKash transaction ID has already been used.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_202_ACCEPTED)
