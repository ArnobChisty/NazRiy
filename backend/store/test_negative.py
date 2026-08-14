from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .authentication import make_token
from .models import Category, Product


class AuthenticationNegativeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "negative-buyer",
            "negative@example.com",
            "StrongPass!42",
        )

    def test_registration_rejects_missing_fields(self):
        response = self.client.post("/api/auth/register/", {"username": "missing"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_registration_rejects_duplicate_username_case_insensitively(self):
        response = self.client.post("/api/auth/register/", {
            "username": "NEGATIVE-BUYER",
            "email": "new@example.com",
            "password": "AnotherStrong!42",
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        response = self.client.post("/api/auth/register/", {
            "username": "different-buyer",
            "email": "NEGATIVE@example.com",
            "password": "AnotherStrong!42",
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_rejects_wrong_password(self):
        response = self.client.post("/api/auth/login/", {
            "username": self.user.username,
            "password": "wrong-password",
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("token", response.data)

    def test_protected_endpoint_rejects_tampered_token(self):
        token = make_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}tampered")
        response = self.client.get("/api/auth/me/")
        self.assertIn(response.status_code, (401, 403))


class CommerceNegativeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "negative-shopper",
            "shopper@example.com",
            "StrongPass!42",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {make_token(self.user)}")
        category = Category.objects.create(name="Negative Tests")
        self.product = Product.objects.create(
            category=category,
            name="Limited Dress",
            description="Test",
            price=Decimal("700.00"),
            stock_quantity=2,
            available_sizes=["M"],
            available_colors=["Red"],
        )

    def test_cart_rejects_zero_quantity(self):
        response = self.client.post("/api/cart/", {
            "product_id": self.product.pk,
            "quantity": 0,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_cart_rejects_invalid_size_and_colour(self):
        for field, value in (("size", "XL"), ("color", "Green")):
            with self.subTest(field=field):
                payload = {"product_id": self.product.pk, "quantity": 1, field: value}
                response = self.client.post("/api/cart/", payload, format="json")
                self.assertEqual(response.status_code, 400)

    def test_checkout_rejects_empty_items(self):
        response = self.client.post("/api/orders/checkout/", {
            "name": "Negative Shopper",
            "email": self.user.email,
            "phone": "+8801712345678",
            "address": "12 Test Road",
            "city": "Dhaka",
            "postal_code": "1205",
            "items": [],
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_checkout_rejects_unknown_product_without_creating_order(self):
        response = self.client.post("/api/orders/checkout/", {
            "name": "Negative Shopper",
            "email": self.user.email,
            "phone": "+8801712345678",
            "address": "12 Test Road",
            "city": "Dhaka",
            "postal_code": "1205",
            "items": [{"product_id": 999999, "quantity": 1}],
        }, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user.orders.count(), 0)

    def test_customer_cannot_modify_another_customers_cart_item(self):
        created = self.client.post("/api/cart/", {
            "product_id": self.product.pk,
            "quantity": 1,
        }, format="json")
        other = User.objects.create_user("cart-owner-two", password="StrongPass!42")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {make_token(other)}")

        response = self.client.patch(
            f"/api/cart/{created.data['id']}/",
            {"quantity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
