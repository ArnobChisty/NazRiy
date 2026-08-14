from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import signing
from django.test import RequestFactory, TestCase, override_settings
from rest_framework.exceptions import AuthenticationFailed

from .authentication import SignedTokenAuthentication, make_token
from .models import Category, Order, OrderEmailLog, Payment, Product
from .order_emails import send_order_confirmation
from .repositories import CategoryRepository, ProductRepository
from .templatetags.dashboard_tags import _month_shift


class RepositoryUnitTests(TestCase):
    def setUp(self):
        dresses = Category.objects.create(name="Dresses")
        accessories = Category.objects.create(name="Accessories")
        self.dress = Product.objects.create(
            category=dresses,
            name="Linen Dress",
            short_description="Summer linen",
            description="Lightweight outfit",
            price=Decimal("1500.00"),
            stock_quantity=3,
            available_sizes=["M"],
            available_colors=["Blue"],
            featured=True,
        )
        self.bag = Product.objects.create(
            category=accessories,
            name="Leather Bag",
            description="Everyday accessory",
            price=Decimal("2500.00"),
            stock_quantity=2,
        )
        self.inactive = Product.objects.create(
            category=dresses,
            name="Hidden Dress",
            description="Inactive",
            price=Decimal("500.00"),
            active=False,
            featured=True,
        )

    def test_category_repository_uses_model_ordering(self):
        self.assertEqual(
            list(CategoryRepository.list_categories().values_list("name", flat=True)),
            ["Accessories", "Dresses"],
        )

    def test_product_repository_searches_name_description_and_category(self):
        self.assertEqual(list(ProductRepository.list_products({"search": "linen"})), [self.dress])
        self.assertEqual(list(ProductRepository.list_products({"search": "accessories"})), [self.bag])

    def test_product_repository_combines_filters_and_ordering(self):
        results = ProductRepository.list_products({
            "min_price": "1000",
            "max_price": "2000",
            "size": "M",
            "color": "Blue",
            "ordering": "price_asc",
        })
        self.assertEqual(list(results), [self.dress])

    def test_product_repository_excludes_inactive_products(self):
        self.assertNotIn(self.inactive, ProductRepository.list_products())
        self.assertIsNone(ProductRepository.get_by_slug(self.inactive.slug))

    def test_featured_repository_returns_only_active_featured_products(self):
        self.assertEqual(list(ProductRepository.featured_products()), [self.dress])

    def test_get_by_slug_returns_active_product(self):
        self.assertEqual(ProductRepository.get_by_slug(self.dress.slug), self.dress)


class AuthenticationUnitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("auth-unit", password="StrongPass!42")
        self.factory = RequestFactory()
        self.authentication = SignedTokenAuthentication()

    def request_with_token(self, token):
        return self.factory.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Token {token}")

    def test_authentication_returns_none_without_token_header(self):
        self.assertIsNone(self.authentication.authenticate(self.factory.get("/")))

    def test_authentication_accepts_valid_signed_token(self):
        authenticated_user, auth = self.authentication.authenticate(
            self.request_with_token(make_token(self.user)),
        )
        self.assertEqual(authenticated_user, self.user)
        self.assertIsNone(auth)

    def test_authentication_rejects_malformed_token(self):
        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(self.request_with_token("not-a-token"))

    def test_password_change_invalidates_existing_token(self):
        token = make_token(self.user)
        self.user.set_password("ChangedStrong!42")
        self.user.save(update_fields=["password"])

        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(self.request_with_token(token))

    @override_settings(AUTH_TOKEN_MAX_AGE=-1)
    def test_expired_token_is_rejected(self):
        token = make_token(self.user)
        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(self.request_with_token(token))


class ServiceUnitTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("email-unit", email="email@example.com")
        category = Category.objects.create(name="Email Tests")
        product = Product.objects.create(
            category=category,
            name="Email Dress",
            description="Test",
            price=Decimal("1000.00"),
            stock_quantity=1,
        )
        self.order = Order.objects.create(
            user=user,
            name="Email Buyer",
            email=user.email,
            phone="+8801712345678",
            address="3 Email Road",
            city="Dhaka",
            postal_code="1205",
            subtotal=Decimal("1000.00"),
            delivery_charge=Decimal("80.00"),
            total=Decimal("1080.00"),
        )
        Payment.objects.create(order=self.order, amount=self.order.total)
        self.product = product

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_order_confirmation_success_creates_sent_audit_log(self):
        result = send_order_confirmation(self.order.pk)
        log = OrderEmailLog.objects.get(order=self.order)

        self.assertTrue(result)
        self.assertEqual(log.status, "sent")
        self.assertEqual(log.recipient, self.order.email)

    @patch("store.order_emails.EmailMultiAlternatives.send", side_effect=RuntimeError("SMTP unavailable"))
    def test_order_confirmation_failure_is_audited_without_raising(self, _send):
        result = send_order_confirmation(self.order.pk)
        log = OrderEmailLog.objects.get(order=self.order)

        self.assertFalse(result)
        self.assertEqual(log.status, "failed")
        self.assertEqual(log.error_message, "SMTP unavailable")

    def test_month_shift_handles_year_boundaries(self):
        self.assertEqual(_month_shift(date(2026, 1, 1), -1), date(2025, 12, 1))
        self.assertEqual(_month_shift(date(2026, 12, 1), 1), date(2027, 1, 1))
