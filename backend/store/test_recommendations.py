from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class RecommendationApiTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name='Apparel')
        self.product = Product.objects.create(category=category, name='Current', description='Current', price=100, stock_quantity=2)
        self.related = Product.objects.create(category=category, name='Related', description='Related', price=120, stock_quantity=3)

    def test_related_products_exclude_current_and_prioritize_category(self):
        response = self.client.get(f'/api/products/{self.product.slug}/related/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [self.related.id])

