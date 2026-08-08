from decimal import Decimal

from rest_framework.test import APITestCase

from .models import Category, Product, ProductSizeMeasurement


class ProductSizeChartTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name='Size Chart Clothing')
        self.product = Product.objects.create(
            category=category,
            name='Florence Test Set',
            description='A set with a product-specific size chart.',
            price=Decimal('5000.00'),
            available_sizes=['S', 'M'],
            stock_quantity=3,
        )
        ProductSizeMeasurement.objects.create(
            product=self.product,
            size='S',
            garment_bust=Decimal('36'),
            length=Decimal('30.5'),
            recommended_bust='32-34',
            pant_length=Decimal('38'),
            sort_order=1,
        )

    def test_product_detail_includes_ordered_size_measurements(self):
        response = self.client.get(f'/api/products/{self.product.slug}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available_sizes'], ['S', 'M'])
        self.assertEqual(response.data['size_chart'][0]['size'], 'S')
        self.assertEqual(response.data['size_chart'][0]['garment_bust'], '36.0')
        self.assertEqual(response.data['size_chart'][0]['length'], '30.5')
        self.assertEqual(response.data['size_chart'][0]['recommended_bust'], '32-34')
        self.assertEqual(response.data['size_chart'][0]['pant_length'], '38.0')
