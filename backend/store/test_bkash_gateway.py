from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase

from .authentication import make_token
from .bkash_gateway import BkashGatewayError
from .models import Order, Payment


GATEWAY_SETTINGS = {
    'BKASH_GATEWAY_ENABLED': True,
    'BKASH_GATEWAY_ENVIRONMENT': 'sandbox',
    'BKASH_GATEWAY_APP_KEY': 'test-app-key',
    'BKASH_GATEWAY_APP_SECRET': 'test-app-secret',
    'BKASH_GATEWAY_USERNAME': 'test-user',
    'BKASH_GATEWAY_PASSWORD': 'test-password',
    'BKASH_GATEWAY_CALLBACK_URL': 'https://api.example.com/api/payments/bkash/callback/',
    'FRONTEND_URL': 'https://shop.example.com',
}


@override_settings(**GATEWAY_SETTINGS)
class BkashGatewayApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('gateway-buyer', password='StrongPass!42')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}')
        self.order = Order.objects.create(
            user=self.user,
            name='Gateway Buyer',
            email='gateway@example.com',
            phone='+8801712345678',
            address='12 Gateway Road',
            city='Dhaka',
            postal_code='1205',
            subtotal=Decimal('1200.00'),
            delivery_charge=Decimal('80.00'),
            total=Decimal('1280.00'),
        )
        self.payment = Payment.objects.create(
            order=self.order,
            method='bkash',
            amount=self.order.total,
        )

    def test_configuration_reports_automated_without_exposing_credentials(self):
        response = self.client.get('/api/payments/bkash/config/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mode'], 'automated')
        self.assertTrue(response.data['automated'])
        self.assertNotIn('app_key', response.data)
        self.assertNotIn('password', response.data)

    @patch('store.bkash_gateway_views.BkashGateway.create_payment')
    def test_create_payment_is_idempotent_and_returns_hosted_checkout(self, create_payment):
        create_payment.return_value = {
            'statusCode': '0000',
            'statusMessage': 'Successful',
            'paymentID': 'TR0011abc',
            'bkashURL': 'https://sandbox.example.com/checkout/TR0011abc',
        }
        endpoint = f'/api/orders/{self.order.pk}/payment/bkash/create/'
        first = self.client.post(endpoint, {}, format='json')
        second = self.client.post(endpoint, {}, format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['redirect_url'], 'https://sandbox.example.com/checkout/TR0011abc')
        self.assertEqual(create_payment.call_count, 1)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.provider_payment_id, 'TR0011abc')
        self.assertEqual(self.payment.attempts, 1)

    @patch('store.bkash_gateway_views.BkashGateway.create_payment')
    def test_provider_failure_does_not_create_a_fake_paid_payment(self, create_payment):
        create_payment.side_effect = BkashGatewayError('Provider unavailable')
        response = self.client.post(
            f'/api/orders/{self.order.pk}/payment/bkash/create/', {}, format='json',
        )
        self.assertEqual(response.status_code, 502)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'pending')
        self.assertFalse(self.payment.provider_payment_id)

    @patch('store.bkash_gateway_views.BkashGateway.verify_completed_payment')
    def test_verified_callback_marks_matching_payment_paid(self, verify_payment):
        self.payment.provider_payment_id = 'TR0011paid'
        self.payment.provider_invoice = 'NR-verified-order'
        self.payment.save()
        verify_payment.return_value = {
            'statusCode': '0000',
            'transactionStatus': 'Completed',
            'paymentID': 'TR0011paid',
            'trxID': 'BKA7ABC123',
            'amount': '1280.00',
            'currency': 'BDT',
            'merchantInvoiceNumber': 'NR-verified-order',
        }
        self.client.credentials()
        response = self.client.get(
            '/api/payments/bkash/callback/?paymentID=TR0011paid&status=success',
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'https://shop.example.com/orders/{self.order.pk}?payment=success')
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')
        self.assertEqual(self.payment.provider_reference, 'BKA7ABC123')

    @patch('store.bkash_gateway_views.BkashGateway.verify_completed_payment')
    def test_callback_rejects_amount_mismatch(self, verify_payment):
        self.payment.provider_payment_id = 'TR0011wrong'
        self.payment.provider_invoice = 'NR-correct'
        self.payment.save()
        verify_payment.return_value = {
            'statusCode': '0000',
            'transactionStatus': 'Completed',
            'paymentID': 'TR0011wrong',
            'trxID': 'BKA7WRONG1',
            'amount': '1.00',
            'merchantInvoiceNumber': 'NR-correct',
        }
        self.client.credentials()
        response = self.client.get(
            '/api/payments/bkash/callback/?paymentID=TR0011wrong&status=success',
        )
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertFalse(self.payment.provider_reference)


class BkashGatewayFallbackTests(APITestCase):
    @override_settings(
        BKASH_GATEWAY_ENABLED=False,
        BKASH_MERCHANT_NUMBER='01700000000',
    )
    def test_manual_mode_remains_available_without_gateway_credentials(self):
        response = self.client.get('/api/payments/bkash/config/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mode'], 'manual')
        self.assertTrue(response.data['manual'])
        self.assertFalse(response.data['automated'])
