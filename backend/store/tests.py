from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductApiTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name="Ceramics")
        self.product = Product.objects.create(
            category=category,
            name="Solace Vase",
            short_description="A calm handmade vase.",
            description="A calm handmade vase for everyday spaces.",
            price=480,
            available_sizes=["Small", "Large"],
            available_colors=["Sand"],
            stock_quantity=8,
            featured=True,
        )

    def test_product_list_and_search(self):
        response = self.client.get(reverse("product-list"), {"search": "Solace"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_detail(self):
        response = self.client.get(reverse("product-detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Solace Vase")

    def test_product_availability_is_fresh_and_not_cached(self):
        url = reverse("product-availability", args=[self.product.slug])
        available = self.client.get(url)
        self.assertEqual(available.status_code, status.HTTP_200_OK)
        self.assertTrue(available.data["in_stock"])
        self.assertIn("no-store", available["Cache-Control"])

        self.product.stock_quantity = 0
        self.product.save(update_fields=["stock_quantity"])
        unavailable = self.client.get(url)
        self.assertFalse(unavailable.data["in_stock"])
        self.assertEqual(unavailable.data["stock_quantity"], 0)

    def test_featured_products(self):
        response = self.client.get(reverse("featured-products"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
