from django.urls import reverse
from rest_framework.test import APITestCase

from .models import NavigationLink


class NavigationLinkApiTests(APITestCase):
    def setUp(self):
        NavigationLink.objects.all().delete()

    def test_lists_only_active_links_in_admin_order(self):
        NavigationLink.objects.create(label='Women', url='/products?category=women', sort_order=2, active=True)
        NavigationLink.objects.create(label='Hidden', url='/hidden', sort_order=1, active=False)
        NavigationLink.objects.create(label='Shop all', url='/products', sort_order=1, active=True)

        response = self.client.get(reverse('navigation-links'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['label'] for item in response.data], ['Shop all', 'Women'])
        self.assertNotIn('active', response.data[0])
