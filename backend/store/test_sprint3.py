from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .authentication import make_token
from .models import Category,Order,Product
class Sprint3Tests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user('buyer','buyer@example.com','StrongPass!42');self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}');category=Category.objects.create(name='Sprint 3');self.product=Product.objects.create(category=category,name='Vase',description='Test',price=1000,stock_quantity=2)
    def test_protected_current_user(self):self.assertEqual(self.client.get('/api/auth/me/').status_code,200)
    def test_cart_rejects_excess_stock(self):self.assertEqual(self.client.post('/api/cart/',{'product_id':self.product.id,'quantity':3},format='json').status_code,400)
    def test_checkout_saves_order_calculates_total_and_reduces_stock(self):
        payload={'name':'Buyer','email':'buyer@example.com','phone':'+8801712345678','address':'12 Road','city':'Dhaka','postal_code':'1205','items':[{'product_id':self.product.id,'quantity':2}]};response=self.client.post('/api/orders/checkout/',payload,format='json');self.assertEqual(response.status_code,201);self.assertEqual(Order.objects.get().total,2000);self.product.refresh_from_db();self.assertEqual(self.product.stock_quantity,0)
    def test_order_history_requires_authentication(self):self.client.credentials();self.assertEqual(self.client.get('/api/orders/').status_code,403)
