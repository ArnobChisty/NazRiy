from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from .authentication import make_token
from .models import Category, Order, OrderItem, Product


class Sprint4Tests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('buyer4', 'buyer4@example.com', 'StrongPass!42')
        self.other = User.objects.create_user('other4', 'other4@example.com', 'StrongPass!42')
        self.token = make_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        category = Category.objects.create(name='Sprint 4')
        self.product = Product.objects.create(
            category=category, name='Tracked Vase', description='Test', price=Decimal('500'), stock_quantity=3,
        )
        self.order = Order.objects.create(
            user=self.user, name='Buyer Four', email='buyer4@example.com', phone='+8801712345678',
            address='12 Road', city='Dhaka', postal_code='1205', subtotal=Decimal('500'),
            delivery_charge=Decimal('80'), total=Decimal('580'),
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, product_name=self.product.name,
            unit_price=Decimal('500'), quantity=1, line_total=Decimal('500'),
        )
        self.other_order = Order.objects.create(
            user=self.other, name='Other Buyer', email='other4@example.com', phone='+8801812345678',
            address='99 Road', city='Dhaka', postal_code='1205', subtotal=Decimal('500'),
            delivery_charge=Decimal('80'), total=Decimal('580'),
        )

    def test_order_list_and_detail_enforce_ownership(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.order.id])
        self.assertEqual(self.client.get(f'/api/orders/{self.order.id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/orders/{self.other_order.id}/').status_code, 404)

    def test_profile_update_validates_unique_email(self):
        response = self.client.patch('/api/auth/profile/', {
            'first_name': 'Updated', 'last_name': 'Buyer', 'email': 'updated@example.com',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.get_full_name(), 'Updated Buyer')
        duplicate = self.client.patch('/api/auth/profile/', {'email': self.other.email}, format='json')
        self.assertEqual(duplicate.status_code, 400)

    def test_password_change_requires_current_password_and_rotates_token(self):
        invalid = self.client.post('/api/auth/password/change/', {
            'current_password': 'wrong', 'new_password': 'AnotherStrong!42', 'confirm_password': 'AnotherStrong!42',
        }, format='json')
        self.assertEqual(invalid.status_code, 400)
        changed = self.client.post('/api/auth/password/change/', {
            'current_password': 'StrongPass!42', 'new_password': 'AnotherStrong!42', 'confirm_password': 'AnotherStrong!42',
        }, format='json')
        self.assertEqual(changed.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {changed.data['token']}")
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 200)

    def test_order_status_transitions_and_cancelled_inventory(self):
        self.order.status = 'cancelled'
        self.order.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 4)
        self.order.status = 'shipped'
        with self.assertRaises(ValidationError):
            self.order.save()

    def test_sprint4_endpoints_require_authentication(self):
        self.client.credentials()
        for url in ['/api/orders/', f'/api/orders/{self.order.id}/', '/api/auth/profile/', '/api/auth/password/change/']:
            response = self.client.get(url) if 'password' not in url else self.client.post(url, {}, format='json')
            self.assertIn(response.status_code, (401, 403))
