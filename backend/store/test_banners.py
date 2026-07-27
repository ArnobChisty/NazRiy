from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from .models import Banner
class BannerApiTests(APITestCase):
    def setUp(self):Banner.objects.all().delete()
    def banner(self,**kwargs):return Banner.objects.create(title=kwargs.pop('title','Campaign'),image_alt='Campaign',desktop_image='banners/desktop/test.jpg',**kwargs)
    def test_active_hero_banners_are_ordered(self):
        self.banner(title='Second',sort_order=2);self.banner(title='First',sort_order=1);response=self.client.get('/api/banners/?placement=hero');self.assertEqual(response.status_code,200);self.assertEqual([item['title'] for item in response.data],['First','Second'])
    def test_inactive_and_expired_banners_are_hidden(self):
        self.banner(title='Inactive',active=False);self.banner(title='Expired',ends_at=timezone.now()-timedelta(days=1));self.assertEqual(self.client.get('/api/banners/').data,[])
