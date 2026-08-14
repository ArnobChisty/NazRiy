from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    Banner,
    Cart,
    Category,
    NavigationLink,
    Order,
    Payment,
    Product,
    ProductImage,
    ProductSizeMeasurement,
    TopProduct,
)


class ModelBehaviourUnitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("model-buyer", password="StrongPass!42")
        self.category = Category.objects.create(name="Model Tests")
        self.product = Product.objects.create(
            category=self.category,
            name="Model Dress",
            description="Model test fixture",
            price=Decimal("1000.00"),
            stock_quantity=4,
        )

    def create_order(self, status="confirmed"):
        return Order.objects.create(
            user=self.user,
            name="Model Buyer",
            email="model@example.com",
            phone="+8801712345678",
            address="1 Model Road",
            city="Dhaka",
            postal_code="1205",
            subtotal=Decimal("1000.00"),
            delivery_charge=Decimal("80.00"),
            total=Decimal("1080.00"),
            status=status,
        )

    def test_related_model_string_labels_are_human_readable(self):
        image = ProductImage(product=self.product, position=1)
        measurement = ProductSizeMeasurement(
            product=self.product,
            size="M",
            garment_bust=Decimal("40.0"),
            length=Decimal("44.0"),
            recommended_bust="36-38",
            pant_length=Decimal("39.0"),
        )
        placement = TopProduct(product=self.product)
        cart = Cart(user=self.user)

        self.assertEqual(str(image), "Model Dress image 2")
        self.assertEqual(str(measurement), "Model Dress - M")
        self.assertEqual(str(placement), "Model Dress")
        self.assertEqual(str(cart), "Cart for model-buyer")

    def test_banner_string_includes_placement_and_title(self):
        banner = Banner(placement="hero", title="New collection")
        self.assertEqual(str(banner), "Homepage hero: New collection")

    def test_non_women_navigation_link_remains_unchanged(self):
        url = "/products?category=accessories"
        self.assertEqual(NavigationLink.canonical_url("Accessories", url), url)

    def test_women_navigation_link_handles_encoded_and_mixed_case_url(self):
        result = NavigationLink.canonical_url(
            " women ",
            "/PRODUCTS?CATEGORY=Women%27s+Clothing",
        )
        self.assertEqual(result, "/products?view=women")

    def test_order_allows_confirmed_to_shipped_to_delivered(self):
        order = self.create_order()
        order.status = "shipped"
        order.save()
        order.status = "delivered"
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")

    def test_delivered_order_cannot_return_to_shipped(self):
        order = self.create_order(status="delivered")
        order.status = "shipped"
        with self.assertRaises(ValidationError):
            order.save()

    def test_payment_string_displays_order_and_status(self):
        order = self.create_order()
        payment = Payment.objects.create(order=order, amount=order.total)
        self.assertEqual(str(payment), f"Payment for order #{order.pk}: Pending")

    def test_cancelled_order_payment_cannot_be_paid(self):
        order = self.create_order(status="cancelled")
        with self.assertRaises(ValidationError):
            Payment.objects.create(order=order, amount=order.total, status="paid")
