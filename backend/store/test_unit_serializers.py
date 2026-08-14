import uuid
from decimal import Decimal

from django.test import TestCase

from .models import Category, Product, ProductImage, ProductSizeMeasurement
from .serializers import ProductSerializer
from .sprint3_serializers import CartItemSerializer, CheckoutSerializer
from .sprint5_serializers import PaymentActionSerializer


class SerializerValidationUnitTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Serializer Boundaries")
        self.product = Product.objects.create(
            category=self.category,
            name="Boundary Dress",
            short_description="A serializer fixture",
            description="Test",
            price=Decimal("750.00"),
            stock_quantity=2,
            available_sizes=["S", "M"],
            available_colors=["Black", "White"],
        )

    def cart_serializer(self, **overrides):
        data = {
            "product_id": self.product.pk,
            "quantity": 1,
            "size": "S",
            "color": "Black",
        }
        data.update(overrides)
        return CartItemSerializer(data=data)

    def test_cart_item_rejects_quantity_below_one(self):
        serializer = self.cart_serializer(quantity=0)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_cart_item_rejects_quantity_above_stock(self):
        serializer = self.cart_serializer(quantity=3)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_cart_item_rejects_unavailable_size(self):
        serializer = self.cart_serializer(size="XL")
        self.assertFalse(serializer.is_valid())

    def test_cart_item_rejects_unavailable_colour(self):
        serializer = self.cart_serializer(color="Green")
        self.assertFalse(serializer.is_valid())

    def checkout_data(self, **overrides):
        data = {
            "name": "Serializer Buyer",
            "email": "serializer@example.com",
            "phone": "+8801712345678",
            "address": "2 Test Road",
            "city": "Dhaka",
            "postal_code": "1205",
            "items": [{"product_id": self.product.pk, "quantity": 1}],
        }
        data.update(overrides)
        return data

    def test_checkout_applies_payment_and_idempotency_defaults(self):
        serializer = CheckoutSerializer(data=self.checkout_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["payment_method"], "bkash")
        self.assertIsInstance(serializer.validated_data["idempotency_key"], uuid.UUID)

    def test_checkout_rejects_invalid_phone(self):
        serializer = CheckoutSerializer(data=self.checkout_data(phone="123"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_checkout_rejects_empty_item_list(self):
        serializer = CheckoutSerializer(data=self.checkout_data(items=[]))
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_payment_cancel_action_does_not_require_transaction_id(self):
        serializer = PaymentActionSerializer(data={
            "action": "cancel",
            "request_id": str(uuid.uuid4()),
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_payment_submit_rejects_short_transaction_id(self):
        serializer = PaymentActionSerializer(data={
            "action": "submit",
            "transaction_id": "ABC123",
            "request_id": str(uuid.uuid4()),
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("transaction_id", serializer.errors)

    def test_product_serializer_includes_gallery_and_size_chart(self):
        ProductImage.objects.create(
            product=self.product,
            image="products/gallery/detail.jpg",
            position=0,
        )
        ProductSizeMeasurement.objects.create(
            product=self.product,
            size="S",
            garment_bust=Decimal("38.0"),
            length=Decimal("42.0"),
            recommended_bust="32-34",
            pant_length=Decimal("38.0"),
        )

        data = ProductSerializer(self.product).data

        self.assertEqual(len(data["additional_images"]), 1)
        self.assertIn("products/gallery/detail.jpg", data["additional_images"][0])
        self.assertEqual(data["size_chart"][0]["size"], "S")
        self.assertTrue(data["in_stock"])
