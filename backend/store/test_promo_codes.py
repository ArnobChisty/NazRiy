import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from .authentication import make_token
from .discounts import DiscountValidationError, quote_discount
from .models import Category, DiscountCampaign, Order, Product


class PromoCodeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('promo-buyer', 'promo@example.com', 'StrongPass!42')
        self.other_user = User.objects.create_user('promo-other', 'promo-other@example.com', 'StrongPass!42')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}')
        category = Category.objects.create(name='Promo products')
        self.product = Product.objects.create(
            category=category,
            name='Promo Test Set',
            description='Promo fixture',
            price=Decimal('1000.00'),
            stock_quantity=20,
            available_sizes=['M'],
            available_colors=['Pink'],
        )
        self.campaign = DiscountCampaign.objects.create(
            name='Launch discount',
            title='Save ten percent',
            discount_code='SAVE10',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            minimum_order_amount=Decimal('500.00'),
            maximum_discount_amount=Decimal('250.00'),
            usage_limit=10,
            per_customer_limit=1,
            active=True,
        )

    def items(self, quantity=1):
        return [{'product_id': self.product.id, 'quantity': quantity, 'size': 'M', 'color': 'Pink'}]

    def checkout_payload(self, *, code='SAVE10', quantity=1, key=None):
        return {
            'name': 'Promo Buyer',
            'email': self.user.email,
            'phone': '+8801712345678',
            'address': '12 Test Road',
            'city': 'Dhaka',
            'postal_code': '1205',
            'payment_method': 'cash_on_delivery',
            'idempotency_key': str(key or uuid.uuid4()),
            'promo_code': code,
            'items': self.items(quantity),
        }

    def test_percentage_quote_is_case_insensitive_and_respects_cap(self):
        quote = quote_discount(code='save10', subtotal=Decimal('3000.00'), user=self.user)

        self.assertEqual(quote.code, 'SAVE10')
        self.assertEqual(quote.discount_amount, Decimal('250.00'))
        self.assertEqual(quote.delivery_charge, Decimal('0.00'))
        self.assertEqual(quote.total, Decimal('2750.00'))

    def test_free_delivery_discount_uses_the_delivery_charge(self):
        campaign = DiscountCampaign.objects.create(
            name='Delivery offer', title='Free delivery', discount_code='SHIPFREE',
            discount_type='free_delivery', discount_value=Decimal('0.00'), per_customer_limit=2,
        )

        quote = quote_discount(code=campaign.discount_code, subtotal=Decimal('1000.00'), user=self.user)

        self.assertEqual(quote.delivery_charge, Decimal('80.00'))
        self.assertEqual(quote.discount_amount, Decimal('80.00'))
        self.assertEqual(quote.total, Decimal('1000.00'))

    def test_validation_endpoint_returns_server_calculated_total(self):
        response = self.client.post('/api/discounts/validate/', {
            'code': 'save10', 'items': self.items(),
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'SAVE10')
        self.assertEqual(response.data['subtotal'], '1000.00')
        self.assertEqual(response.data['delivery_charge'], '80.00')
        self.assertEqual(response.data['discount_amount'], '100.00')
        self.assertEqual(response.data['total'], '980.00')

    def test_validation_rejects_invalid_expired_and_minimum_spend_codes(self):
        invalid = self.client.post('/api/discounts/validate/', {'code': 'NOPE', 'items': self.items()}, format='json')
        self.campaign.ends_at = timezone.now() - timedelta(minutes=1)
        self.campaign.save(update_fields=['ends_at'])
        expired = self.client.post('/api/discounts/validate/', {'code': 'SAVE10', 'items': self.items()}, format='json')
        self.campaign.ends_at = None
        self.campaign.minimum_order_amount = Decimal('1500.00')
        self.campaign.save(update_fields=['ends_at', 'minimum_order_amount'])
        minimum = self.client.post('/api/discounts/validate/', {'code': 'SAVE10', 'items': self.items()}, format='json')

        self.assertEqual(invalid.status_code, 400)
        self.assertIn('invalid', invalid.data['detail'])
        self.assertEqual(expired.status_code, 400)
        self.assertIn('expired', expired.data['detail'])
        self.assertEqual(minimum.status_code, 400)
        self.assertIn('more', minimum.data['detail'])

    def test_checkout_stores_discount_and_payment_uses_discounted_total(self):
        response = self.client.post('/api/orders/checkout/', self.checkout_payload(), format='json')

        self.assertEqual(response.status_code, 201)
        order = Order.objects.select_related('payment', 'discount_campaign').get(pk=response.data['id'])
        self.assertEqual(order.discount_campaign, self.campaign)
        self.assertEqual(order.discount_code, 'SAVE10')
        self.assertEqual(order.discount_amount, Decimal('100.00'))
        self.assertEqual(order.total, Decimal('980.00'))
        self.assertEqual(order.payment.amount, Decimal('980.00'))

    def test_checkout_revalidates_code_and_enforces_customer_limit(self):
        first = self.client.post('/api/orders/checkout/', self.checkout_payload(), format='json')
        second = self.client.post('/api/orders/checkout/', self.checkout_payload(), format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertIn('already used', second.data['detail'])
        self.assertEqual(Order.objects.count(), 1)

    def test_idempotent_retry_returns_original_discounted_order(self):
        key = uuid.uuid4()
        first = self.client.post('/api/orders/checkout/', self.checkout_payload(key=key), format='json')
        second = self.client.post('/api/orders/checkout/', self.checkout_payload(key=key), format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['id'], second.data['id'])

    def test_global_usage_limit_is_enforced(self):
        self.campaign.usage_limit = 1
        self.campaign.save(update_fields=['usage_limit'])
        self.client.post('/api/orders/checkout/', self.checkout_payload(), format='json')
        with self.assertRaisesRegex(DiscountValidationError, 'usage limit'):
            quote_discount(code='SAVE10', subtotal=Decimal('1000.00'), user=self.other_user)

    def test_validation_requires_authentication(self):
        self.client.credentials()
        response = self.client.post('/api/discounts/validate/', {
            'code': 'SAVE10', 'items': self.items(),
        }, format='json')

        self.assertEqual(response.status_code, 403)

    def test_discount_cannot_create_a_zero_total_order(self):
        self.campaign.discount_type = 'fixed'
        self.campaign.discount_value = Decimal('2000.00')
        self.campaign.maximum_discount_amount = None
        self.campaign.save(update_fields=['discount_type', 'discount_value', 'maximum_discount_amount'])

        with self.assertRaisesRegex(DiscountValidationError, 'zero'):
            quote_discount(code='SAVE10', subtotal=Decimal('2000.00'), user=self.user)

    def test_checkout_aggregates_stock_across_product_options(self):
        self.product.stock_quantity = 3
        self.product.available_sizes = ['M', 'L']
        self.product.save(update_fields=['stock_quantity', 'available_sizes'])
        payload = self.checkout_payload(code='')
        payload['items'] = [
            {'product_id': self.product.id, 'quantity': 2, 'size': 'M', 'color': 'Pink'},
            {'product_id': self.product.id, 'quantity': 2, 'size': 'L', 'color': 'Pink'},
        ]

        response = self.client.post('/api/orders/checkout/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('selected options', response.data['detail'])
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)
        self.assertFalse(Order.objects.exists())


class PromoCodeModelTests(APITestCase):
    def test_codes_must_be_unique_case_insensitively(self):
        first = DiscountCampaign(name='First', title='First', discount_code='SAVE20')
        first.full_clean()
        first.save()
        duplicate = DiscountCampaign(name='Second', title='Second', discount_code='save20')

        with self.assertRaisesRegex(Exception, 'already used'):
            duplicate.full_clean()
