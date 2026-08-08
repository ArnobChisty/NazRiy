from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase
from .authentication import make_token
from .models import Category,Order,OrderEmailLog,Product
class Sprint3Tests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user('buyer','buyer@example.com','StrongPass!42');self.client.credentials(HTTP_AUTHORIZATION=f'Token {make_token(self.user)}');category=Category.objects.create(name='Sprint 3');self.product=Product.objects.create(category=category,name='Vase',description='Test',price=1000,stock_quantity=2)
    def test_protected_current_user(self):self.assertEqual(self.client.get('/api/auth/me/').status_code,200)
    def test_cart_rejects_excess_stock(self):self.assertEqual(self.client.post('/api/cart/',{'product_id':self.product.id,'quantity':3},format='json').status_code,400)
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', FRONTEND_URL='https://nazriy.example')
    def test_checkout_saves_order_calculates_total_reduces_stock_and_emails_customer(self):
        payload={'name':'Buyer','email':'buyer@example.com','phone':'+8801712345678','address':'12 Road','city':'Dhaka','postal_code':'1205','items':[{'product_id':self.product.id,'quantity':2}]}
        with self.captureOnCommitCallbacks(execute=True):response=self.client.post('/api/orders/checkout/',payload,format='json')
        order=Order.objects.get();self.assertEqual(response.status_code,201);self.assertEqual(order.total,2000);self.product.refresh_from_db();self.assertEqual(self.product.stock_quantity,0)
        self.assertEqual(len(mail.outbox),1);self.assertIn(f'order #{order.id} confirmed',mail.outbox[0].subject.lower());self.assertEqual(mail.outbox[0].to,['buyer@example.com']);self.assertEqual(OrderEmailLog.objects.get().status,'sent')
    def test_order_history_requires_authentication(self):self.client.credentials();self.assertEqual(self.client.get('/api/orders/').status_code,403)
    def test_checkout_normalizes_legacy_default_colour(self):
        self.product.available_colors=['Red'];self.product.save(update_fields=['available_colors'])
        payload={'name':'Buyer','email':'buyer@example.com','phone':'+8801712345678','address':'12 Road','city':'Dhaka','postal_code':'1205','payment_method':'cash_on_delivery','items':[{'product_id':self.product.id,'quantity':1,'color':'Default'}]}
        response=self.client.post('/api/orders/checkout/',payload,format='json')
        self.assertEqual(response.status_code,201);self.assertEqual(Order.objects.get().items.get().color,'Red')
