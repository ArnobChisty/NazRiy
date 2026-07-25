from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Category, Product, TopProduct


class TopProductApiTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name='Clothing')
        self.first = Product.objects.create(category=category, name='First set', description='First', price=Decimal('1000'), stock_quantity=2)
        self.second = Product.objects.create(category=category, name='Second set', description='Second', price=Decimal('1200'), stock_quantity=2)

    def test_lists_only_active_admin_selections_in_order(self):
        TopProduct.objects.create(product=self.first, sort_order=2, active=True)
        TopProduct.objects.create(product=self.second, sort_order=1, active=False)

        response = self.client.get(reverse('top-products'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product']['slug'], self.first.slug)
        self.assertEqual(response.data[0]['sort_order'], 2)
