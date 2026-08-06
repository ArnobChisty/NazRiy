import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from .authentication import make_token
from .models import Category, Order, Payment, Product


class Sprint5PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('sprint5-buyer', 'sprint5@example.com', 'StrongPass!42')
        self.other = User.objects.create_user('sprint5-other', 'other5@example.com', 'StrongPass!42')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}')
        category = Category.objects.create(name='Sprint 5')
        self.product = Product.objects.create(
            category=category,
            name='bKash Test Set',
            description='Sprint 5 payment fixture',
            price=Decimal('1000.00'),
            stock_quantity=5,
            available_sizes=['M'],
            available_colors=['Red'],
        )

    def checkout_payload(self, *, key=None, method='bkash'):
        return {
            'name': 'Sprint Five Buyer',
            'email': self.user.email,
            'phone': '+8801712345678',
            'address': '12 Test Road',
            'city': 'Dhaka',
            'postal_code': '1205',
            'payment_method': method,
            'idempotency_key': str(key or uuid.uuid4()),
            'items': [{'product_id': self.product.id, 'quantity': 2, 'size': 'M', 'color': 'Red'}],
        }

    def create_order(self, **kwargs):
        response = self.client.post('/api/orders/checkout/', self.checkout_payload(**kwargs), format='json')
        self.assertEqual(response.status_code, 201)
        return Order.objects.get(pk=response.data['id'])

    def payment_action(self, order, *, action='submit', transaction_id='BK7A1B2C3D', request_id=None):
        payload = {
            'action': action,
            'request_id': str(request_id or uuid.uuid4()),
        }
        if action == 'submit':
            payload['transaction_id'] = transaction_id
        return self.client.post(f'/api/orders/{order.id}/payment/', payload, format='json')

    def test_checkout_creates_pending_bkash_payment_with_server_total(self):
        order = self.create_order()
        self.assertEqual(order.total, Decimal('2000.00'))
        self.assertEqual(order.payment.amount, order.total)
        self.assertEqual(order.payment.method, 'bkash')
        self.assertEqual(order.payment.status, 'pending')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)

    def test_checkout_idempotency_prevents_duplicate_orders_and_stock_updates(self):
        key = uuid.uuid4()
        first = self.client.post('/api/orders/checkout/', self.checkout_payload(key=key), format='json')
        second = self.client.post('/api/orders/checkout/', self.checkout_payload(key=key), format='json')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertEqual(Order.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)

    def test_bkash_transaction_submission_is_pending_and_idempotent(self):
        order = self.create_order()
        request_id = uuid.uuid4()
        first = self.payment_action(order, request_id=request_id)
        second = self.payment_action(order, request_id=request_id)
        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 200)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.status, 'pending')
        self.assertEqual(order.payment.attempts, 1)
        self.assertEqual(order.payment.provider_reference, 'BK7A1B2C3D')

    def test_duplicate_bkash_transaction_id_is_rejected(self):
        first_order = self.create_order()
        self.assertEqual(self.payment_action(first_order).status_code, 202)
        self.product.stock_quantity = 5
        self.product.save(update_fields=['stock_quantity'])
        second_order = self.create_order()
        duplicate = self.payment_action(second_order, transaction_id='bk7a1b2c3d')
        self.assertEqual(duplicate.status_code, 409)

    def test_invalid_bkash_transaction_id_is_rejected(self):
        order = self.create_order()
        response = self.payment_action(order, transaction_id='bad id')
        self.assertEqual(response.status_code, 400)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.provider_reference, '')

    def test_rejected_bkash_payment_can_submit_a_new_transaction(self):
        order = self.create_order()
        self.assertEqual(self.payment_action(order).status_code, 202)
        order.payment.status = 'failed'
        order.payment.failure_reason = 'Could not verify the transaction.'
        order.payment.save()
        resubmitted = self.payment_action(order, transaction_id='NEW1234567')
        self.assertEqual(resubmitted.status_code, 202)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.status, 'pending')
        self.assertEqual(order.payment.provider_reference, 'NEW1234567')
        self.assertEqual(order.payment.attempts, 2)

    def test_cancelling_payment_cancels_order_and_restores_stock(self):
        order = self.create_order()
        cancelled = self.payment_action(order, action='cancel')
        self.assertEqual(cancelled.status_code, 200)
        order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')
        self.assertEqual(order.payment.status, 'cancelled')
        self.assertEqual(self.product.stock_quantity, 5)

    def test_payment_endpoint_enforces_order_ownership(self):
        order = self.create_order()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.other)}')
        self.assertEqual(self.payment_action(order).status_code, 404)

    def test_cash_on_delivery_rejects_bkash_submission(self):
        order = self.create_order(method='cash_on_delivery')
        response = self.payment_action(order)
        self.assertEqual(response.status_code, 400)
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.status, 'pending')

    def test_payment_amount_must_match_order_total(self):
        order = self.create_order()
        payment = order.payment
        payment.amount = Decimal('1.00')
        with self.assertRaises(ValidationError):
            payment.save()

    def test_payment_endpoint_requires_authentication(self):
        order = self.create_order()
        self.client.credentials()
        self.assertIn(self.payment_action(order).status_code, (401, 403))
