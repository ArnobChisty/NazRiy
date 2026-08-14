from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DiscountCampaign


class DiscountCampaignTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'campaign-admin', 'campaign-admin@example.com', 'safe-password-123'
        )

    def test_public_endpoint_returns_only_active_campaigns_in_schedule(self):
        now = timezone.now()
        live = DiscountCampaign.objects.create(
            name='Live sale', display_type='announcement', title='Save 20%',
            discount_code='SAVE20', starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(hours=1),
        )
        DiscountCampaign.objects.create(name='Inactive', title='Hidden', active=False)
        DiscountCampaign.objects.create(
            name='Future', title='Later', starts_at=now + timedelta(days=1)
        )
        DiscountCampaign.objects.create(
            name='Ended', title='Finished', ends_at=now - timedelta(minutes=1)
        )

        response = self.client.get(reverse('discount-campaigns'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.json()], [live.id])
        self.assertEqual(response.json()[0]['discount_code'], 'SAVE20')
        self.assertIn('s-maxage=30', response.headers['Cache-Control'])

    def test_campaign_rejects_an_end_before_its_start(self):
        now = timezone.now()
        campaign = DiscountCampaign(
            name='Invalid schedule', title='Invalid', starts_at=now,
            ends_at=now - timedelta(minutes=1),
        )

        with self.assertRaises(ValidationError):
            campaign.full_clean()

    def test_admin_has_discount_module_and_direct_add_shortcut(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:store_discountcampaign_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Discount campaigns')
        self.assertContains(response, reverse('admin:store_discountcampaign_add'))
        self.assertContains(response, 'aria-label="Add discount campaign"')

    def test_admin_add_pages_render_without_existing_images(self):
        self.client.force_login(self.admin_user)

        discount_response = self.client.get(reverse('admin:store_discountcampaign_add'))
        banner_response = self.client.get(reverse('admin:store_banner_add'))

        self.assertEqual(discount_response.status_code, 200)
        self.assertContains(discount_response, 'once per session')
        self.assertEqual(banner_response.status_code, 200)
        self.assertContains(banner_response, 'Automatic schedule')
