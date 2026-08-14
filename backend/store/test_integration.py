import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase

from .authentication import make_token
from .models import Cart, Category, Order, Payment, Product


class CustomerJourneyIntegrationTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name="Integration Tests")
        self.product = Product.objects.create(
            category=category,
            name="Journey Dress",
            description="Integration fixture",
            price=Decimal("1200.00"),
            stock_quantity=5,
            available_sizes=["M", "L"],
            available_colors=["Red", "Blue"],
        )

    def test_register_token_profile_and_email_login_work_together(self):
        registered = self.client.post("/api/auth/register/", {
            "username": "journey-buyer",
            "email": "Journey@Example.com",
            "password": "StrongJourney!42",
        }, format="json")
        self.assertEqual(registered.status_code, 201)

        token = registered.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        profile = self.client.patch("/api/auth/profile/", {
            "first_name": "Journey",
            "last_name": "Buyer",
            "email": "updated@example.com",
        }, format="json")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data["full_name"], "Journey Buyer")

        self.client.credentials()
        logged_in = self.client.post("/api/auth/login/", {
            "email": "UPDATED@EXAMPLE.COM",
            "password": "StrongJourney!42",
        }, format="json")
        self.assertEqual(logged_in.status_code, 200)
        self.assertIn("token", logged_in.data)

    def test_cart_create_update_list_and_delete_flow(self):
        user = User.objects.create_user("cart-journey", password="StrongPass!42")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {make_token(user)}")

        created = self.client.post("/api/cart/", {
            "product_id": self.product.pk,
            "quantity": 1,
            "size": "M",
            "color": "Red",
        }, format="json")
        self.assertEqual(created.status_code, 201)

        updated = self.client.patch(
            f"/api/cart/{created.data['id']}/",
            {"quantity": 2},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["quantity"], 2)

        listed = self.client.get("/api/cart/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)

        deleted = self.client.delete(f"/api/cart/{created.data['id']}/")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get("/api/cart/").data, [])

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_cart_checkout_order_history_and_inventory_flow(self):
        user = User.objects.create_user(
            "checkout-journey",
            "checkout@example.com",
            "StrongPass!42",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {make_token(user)}")
        self.client.post("/api/cart/", {
            "product_id": self.product.pk,
            "quantity": 2,
            "size": "L",
            "color": "Blue",
        }, format="json")

        payload = {
            "name": "Checkout Journey",
            "email": user.email,
            "phone": "+8801712345678",
            "address": "12 Integration Road",
            "city": "Dhaka",
            "postal_code": "1205",
            "payment_method": "bkash",
            "idempotency_key": str(uuid.uuid4()),
            "items": [{
                "product_id": self.product.pk,
                "quantity": 2,
                "size": "L",
                "color": "Blue",
            }],
        }
        with self.captureOnCommitCallbacks(execute=True):
            checked_out = self.client.post("/api/orders/checkout/", payload, format="json")

        self.assertEqual(checked_out.status_code, 201)
        order = Order.objects.get(pk=checked_out.data["id"])
        self.assertEqual(order.subtotal, Decimal("2400.00"))
        self.assertEqual(order.delivery_charge, Decimal("0.00"))
        self.assertEqual(order.total, Decimal("2400.00"))
        self.assertTrue(Payment.objects.filter(order=order, method="bkash").exists())
        self.assertFalse(Cart.objects.filter(user=user).exists())

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)
        history = self.client.get("/api/orders/")
        detail = self.client.get(f"/api/orders/{order.pk}/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.data[0]["id"], order.pk)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["items"][0]["quantity"], 2)
