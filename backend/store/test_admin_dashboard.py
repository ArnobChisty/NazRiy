from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, OrderItem, Product


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
        order = Order.objects.create(
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
            order=order,
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=1,
            line_total=product.price,
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
        self.assertContains(response, 'admin/css/nazriy_admin_global.css')

    def test_analytics_navigation_targets_dashboard_section(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:index'))

        self.assertContains(response, f'{reverse("admin:index")}#analytics')
