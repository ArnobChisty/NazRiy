from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import ProductAdminForm
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

    def test_orders_page_combines_order_and_payment_operations(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:store_order_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orders &amp; payments')
        self.assertContains(response, 'Paid revenue')
        self.assertContains(response, 'Pending payment')
        self.assertContains(response, 'Cash on delivery')
        self.assertContains(response, 'Not required')
        self.assertContains(response, 'Fulfilment')
        self.assertContains(response, 'Recommended workflow')

    def test_payment_model_is_hidden_from_navigation_but_direct_view_remains_available(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:index'))

        self.assertNotContains(response, f'href="{reverse("admin:store_payment_changelist")}"')
        self.assertEqual(self.client.get(reverse('admin:store_payment_changelist')).status_code, 200)

    def test_order_workspace_can_verify_bkash_and_progress_fulfilment(self):
        self.payment.method = 'bkash'
        self.payment.provider_reference = 'BKASH-ADMIN-1001'
        self.payment.save()
        self.client.force_login(self.admin_user)
        url = reverse('admin:store_order_changelist')

        response = self.client.post(url, {
            'action': 'verify_bkash_payments',
            '_selected_action': [self.order.pk],
            'index': '0',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')

        self.client.post(url, {
            'action': 'mark_as_shipped',
            '_selected_action': [self.order.pk],
            'index': '0',
        })
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')

        self.client.post(url, {
            'action': 'mark_as_delivered',
            '_selected_action': [self.order.pk],
            'index': '0',
        })
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

    def test_fulfilment_can_be_progressed_from_the_order_table(self):
        self.client.force_login(self.admin_user)
        url = reverse('admin:store_order_changelist')

        response = self.client.get(url)
        self.assertContains(response, f'value="ship:{self.order.pk}"')

        response = self.client.post(url, {'_quick_fulfilment': f'ship:{self.order.pk}'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')
        self.assertContains(response, f'value="deliver:{self.order.pk}"')

        self.client.post(url, {'_quick_fulfilment': f'deliver:{self.order.pk}'})
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

    def test_cash_on_delivery_can_be_marked_paid_from_the_order_table(self):
        self.client.force_login(self.admin_user)
        url = reverse('admin:store_order_changelist')

        response = self.client.get(url)
        self.assertContains(response, f'value="collect:{self.order.pk}"')

        response = self.client.post(url, {'_quick_payment': f'collect:{self.order.pk}'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')
        self.assertNotContains(response, f'value="collect:{self.order.pk}"')

    def test_bkash_can_be_verified_from_the_order_table(self):
        self.payment.method = 'bkash'
        self.payment.provider_reference = 'BKASH-QUICK-2001'
        self.payment.save()
        self.client.force_login(self.admin_user)
        url = reverse('admin:store_order_changelist')

        response = self.client.get(url)
        self.assertContains(response, f'value="verify:{self.order.pk}"')
        self.client.post(url, {'_quick_payment': f'verify:{self.order.pk}'})

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')

    def test_catalogue_sidebar_has_direct_add_shortcuts(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:store_product_changelist'))

        self.assertContains(response, reverse('admin:store_product_add'))
        self.assertContains(response, reverse('admin:store_category_add'))
        self.assertContains(response, reverse('admin:store_topproduct_add'))
        self.assertContains(response, 'aria-label="Add product"')

    def test_product_form_uses_simple_comma_separated_options(self):
        product = Product.objects.get(name='NazRiy Test Set')
        form = ProductAdminForm(data={
            'category': product.category_id,
            'name': product.name,
            'slug': product.slug,
            'short_description': '',
            'description': product.description,
            'price': product.price,
            'available_sizes': 'S, M, L, M',
            'available_colors': 'Black, Rose, Ivory',
            'stock_quantity': product.stock_quantity,
            'active': True,
            'featured': False,
            'tone': product.tone,
            'shape': product.shape,
        }, instance=product)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['available_sizes'], ['S', 'M', 'L'])
        self.assertEqual(form.cleaned_data['available_colors'], ['Black', 'Rose', 'Ivory'])

    def test_catalogue_admin_pages_show_business_friendly_fields(self):
        self.client.force_login(self.admin_user)

        product_response = self.client.get(reverse('admin:store_product_change', args=(Product.objects.get(name='NazRiy Test Set').pk,)))
        category_response = self.client.get(reverse('admin:store_category_changelist'))

        self.assertContains(product_response, 'No JSON formatting is required')
        self.assertContains(product_response, 'Add extra product photos in the gallery section below')
        self.assertContains(category_response, 'Products')

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
