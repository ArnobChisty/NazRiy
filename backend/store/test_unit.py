from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import signing
from django.test import TestCase

from .authentication import TOKEN_SALT, make_token
from .models import Category, NavigationLink, Order, Payment, Product
from .sprint3_serializers import CartItemSerializer
from .sprint5_serializers import PaymentActionSerializer


class StoreModelUnitTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Women's Clothing")

    def test_category_generates_slug_and_string_label(self):
        self.assertEqual(self.category.slug, "womens-clothing")
        self.assertEqual(str(self.category), "Women's Clothing")

    def test_products_with_same_name_receive_unique_slugs(self):
        first = Product.objects.create(
            category=self.category,
            name="Cotton Set",
            description="First",
            price=Decimal("1200.00"),
        )
        second = Product.objects.create(
            category=self.category,
            name="Cotton Set",
            description="Second",
            price=Decimal("1300.00"),
        )

        self.assertEqual(first.slug, "cotton-set")
        self.assertEqual(second.slug, "cotton-set-2")

    def test_product_in_stock_reflects_current_quantity(self):
        product = Product.objects.create(
            category=self.category,
            name="Stock Test",
            description="Test",
            price=Decimal("500.00"),
            stock_quantity=0,
        )
        self.assertFalse(product.in_stock)
        product.stock_quantity = 1
        self.assertTrue(product.in_stock)

    def test_women_navigation_link_is_canonicalized(self):
        link = NavigationLink.objects.create(
            label="Women",
            url="/products?category=Women%27s+Clothing",
        )
        self.assertEqual(link.url, "/products?view=women")


class StoreSerializerUnitTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Serializer Tests")
        self.product = Product.objects.create(
            category=category,
            name="Sized Dress",
            description="Test",
            price=Decimal("900.00"),
            stock_quantity=3,
            available_sizes=["M", "L"],
            available_colors=["Red", "Blue"],
        )

    def test_cart_item_serializer_accepts_available_options(self):
        serializer = CartItemSerializer(data={
            "product_id": self.product.pk,
            "quantity": 2,
            "size": "M",
            "color": "Red",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_payment_action_requires_transaction_for_submit(self):
        serializer = PaymentActionSerializer(data={
            "action": "submit",
            "request_id": "18b734f5-1072-49d8-8af1-2bf961afcc0c",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("transaction_id", serializer.errors)

    def test_payment_model_rejects_amount_different_from_order_total(self):
        user = User.objects.create_user("unit-buyer", password="StrongPass!42")
        order = Order.objects.create(
            user=user,
            name="Unit Buyer",
            email="unit@example.com",
            phone="+8801712345678",
            address="1 Test Road",
            city="Dhaka",
            postal_code="1205",
            subtotal=Decimal("900.00"),
            delivery_charge=Decimal("80.00"),
            total=Decimal("980.00"),
        )

        with self.assertRaises(ValidationError):
            Payment.objects.create(order=order, amount=Decimal("1.00"))

    def test_signed_token_contains_valid_user_identity(self):
        user = User.objects.create_user("token-buyer", password="StrongPass!42")
        token = make_token(user)
        payload = signing.loads(token, salt=TOKEN_SALT)

        self.assertEqual(payload["user_id"], user.pk)
        self.assertEqual(payload["auth_hash"], user.get_session_auth_hash())
