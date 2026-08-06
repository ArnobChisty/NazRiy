import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .authentication import make_token
from .models import Category, Product, TopProduct


class Sprint6ReleaseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('release-buyer', password='StrongPass!42')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}')
        self.category = Category.objects.create(name='Release Clothing')
        self.product = Product.objects.create(
            category=self.category,
            name='Release Set',
            description='Release test product',
            price=Decimal('1500.00'),
            stock_quantity=4,
            available_sizes=['M'],
            available_colors=['Red'],
        )

    def test_inactive_products_are_hidden_from_every_public_catalogue_endpoint(self):
        TopProduct.objects.create(product=self.product, active=True)
        self.product.active = False
        self.product.featured = True
        self.product.save()
        self.assertEqual(self.client.get('/api/products/').data, [])
        self.assertEqual(self.client.get('/api/products/featured/').data, [])
        self.assertEqual(self.client.get('/api/top-products/').data, [])
        self.assertEqual(self.client.get(f'/api/products/{self.product.slug}/').status_code, 404)

    def test_checkout_uses_database_price_and_restores_inventory_only_once(self):
        payload = {
            'name': 'Release Buyer', 'email': 'release@example.com', 'phone': '+8801712345678',
            'address': '12 Release Road', 'city': 'Dhaka', 'postal_code': '1205',
            'payment_method': 'bkash', 'idempotency_key': str(uuid.uuid4()),
            'items': [{'product_id': self.product.id, 'quantity': 2, 'size': 'M', 'color': 'Red', 'price': '1.00'}],
        }
        response = self.client.post('/api/orders/checkout/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data['subtotal']), Decimal('3000.00'))
        order_id = response.data['id']
        cancel = {'action': 'cancel', 'request_id': str(uuid.uuid4())}
        self.assertEqual(self.client.post(f'/api/orders/{order_id}/payment/', cancel, format='json').status_code, 200)
        cancel['request_id'] = str(uuid.uuid4())
        self.assertEqual(self.client.post(f'/api/orders/{order_id}/payment/', cancel, format='json').status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 4)

    def test_health_response_never_exposes_credentials(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'status', 'database', 'media_storage'})
