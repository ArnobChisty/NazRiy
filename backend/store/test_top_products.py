from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Banner, Category, NavigationLink, Product, TopProduct


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

    def test_homepage_endpoint_combines_public_content_and_is_edge_cacheable(self):
        self.first.featured = True
        self.first.save(update_fields=['featured'])
        TopProduct.objects.create(product=self.first, active=True)
        Banner.objects.create(title='Campaign', image_alt='Campaign', desktop_image='banners/test.jpg')
        NavigationLink.objects.create(label='Shop all', url='/products', active=True)

        response = self.client.get(reverse('homepage'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['banners'][0]['title'], 'Campaign')
        self.assertEqual(response.data['top_products'][0]['product']['slug'], self.first.slug)
        self.assertEqual(response.data['featured_products'][0]['slug'], self.first.slug)
        self.assertEqual(response.data['navigation_links'][0]['url'], '/products')
        self.assertIn('s-maxage=30', response.headers['Cache-Control'])
        self.assertNotIn('Cookie', response.headers.get('Vary', ''))
