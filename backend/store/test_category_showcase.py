from rest_framework.test import APITestCase

from .models import Category


class CategoryShowcaseTests(APITestCase):
    def test_category_api_exposes_admin_managed_showcase_fields(self):
        Category.objects.all().delete()
        Category.objects.create(
            name='Editorial Clothing', description='Test', featured=True, sort_order=1,
            image='categories/editorial.jpg',
            image_alt='Editorial clothing category',
        )
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['image_alt'], 'Editorial clothing category')
        self.assertTrue(response.data[0]['image'].startswith('http://testserver/media/categories/'))
        self.assertTrue(response.data[0]['featured'])
