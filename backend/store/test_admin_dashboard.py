from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Cart, CartItem, Category, Order, OrderItem, Payment, Product


class AdminDashboardTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            'dashboard-admin',
            'admin@example.com',
            'safe-password-123',
        )
        customer = user_model.objects.create_user(
            'customer',
            'customer@example.com',
            'safe-password-123',
        )
        category = Category.objects.create(name='Clothing')
        product = Product.objects.create(
            category=category,
            name='NazRiy Test Set',
            description='Dashboard test product',
            price=Decimal('5000.00'),
            stock_quantity=3,
        )
        self.order = Order.objects.create(
            user=customer,
            name='Test Customer',
            email='customer@example.com',
            phone='01700000000',
            address='Dhaka',
            city='Dhaka',
            postal_code='1200',
            subtotal=Decimal('5000.00'),
            delivery_charge=Decimal('80.00'),
            total=Decimal('5080.00'),
        )
        OrderItem.objects.create(
            order=self.order,
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=1,
            line_total=product.price,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            method='cash_on_delivery',
            amount=self.order.total,
        )

    def test_admin_index_renders_business_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gross revenue over the last six months')
        self.assertContains(response, 'Top products')
        self.assertContains(response, 'NazRiy Test Set')
        self.assertContains(response, '5080')

    def test_admin_changelist_uses_nazriy_global_theme(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:store_order_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('admin-theme-css'))

    def test_analytics_navigation_targets_dashboard_section(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:index'))

        self.assertContains(response, f'{reverse("admin:index")}#analytics')

    def test_cart_models_are_hidden_from_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:index'))

        self.assertNotIn(Cart, admin.site._registry)
        self.assertNotIn(CartItem, admin.site._registry)
        self.assertNotContains(response, 'Customer carts')

    def test_payment_changelist_is_an_operations_view(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:store_payment_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment operations')
        self.assertContains(response, 'Order #')
        self.assertContains(response, 'Test Customer')
        self.assertContains(response, 'Cash on delivery')
        self.assertContains(response, '৳5,080.00')
        self.assertContains(response, 'Pending')
        self.assertNotContains(response, 'ADD PAYMENT')

    def test_payment_records_cannot_be_manually_created_or_deleted(self):
        self.client.force_login(self.admin_user)

        self.assertEqual(self.client.get(reverse('admin:store_payment_add')).status_code, 403)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=False)
    def test_admin_static_assets_are_available_without_collectstatic(self):
        response = self.client.get('/static/admin/css/base.css')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('text/css'))
        self.assertIn('public', response.headers['Cache-Control'])
