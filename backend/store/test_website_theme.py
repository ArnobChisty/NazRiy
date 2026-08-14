from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import WebsiteThemeAdmin
from .models import WebsiteTheme


class WebsiteThemeTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_defaults_to_dark_without_a_saved_setting(self):
        self.assertEqual(WebsiteTheme.active_theme(), 'dark')

    def test_theme_setting_is_a_singleton(self):
        first = WebsiteTheme.objects.create(theme='white')
        second = WebsiteTheme(theme='pink')
        second.save()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(WebsiteTheme.objects.count(), 1)
        self.assertEqual(WebsiteTheme.active_theme(), 'pink')
        self.assertEqual(str(second), 'Pink website theme')

    def test_public_theme_endpoint_returns_current_selection(self):
        WebsiteTheme.objects.create(theme='white')
        response = self.client.get(reverse('website-theme'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'theme': 'white'})
        self.assertIn('no-store', response['Cache-Control'])

    def test_homepage_response_contains_selected_theme(self):
        WebsiteTheme.objects.create(theme='pink')
        response = self.client.get(reverse('homepage'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['site_theme'], 'pink')

    def test_admin_prevents_extra_records_and_deletion(self):
        admin = WebsiteThemeAdmin(WebsiteTheme, AdminSite())
        request = self.factory.get('/admin/store/websitetheme/')
        request.user = User.objects.create_superuser('theme-admin', 'admin@example.com', 'StrongPass!42')

        setting = WebsiteTheme.objects.get(pk=1)
        self.assertFalse(admin.has_add_permission(request))
        self.assertFalse(admin.has_delete_permission(request, setting))
        self.assertIn('Dark', str(admin.theme_preview(setting)))

    def test_admin_sidebar_links_to_theme_switcher(self):
        admin_user = User.objects.create_superuser('sidebar-admin', 'sidebar@example.com', 'StrongPass!42')
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:index'))

        self.assertContains(response, 'Website theme')
        self.assertContains(response, reverse('admin:store_websitetheme_changelist'))

    def test_admin_changelist_offers_all_theme_choices(self):
        admin_user = User.objects.create_superuser('switcher-admin', 'switcher@example.com', 'StrongPass!42')
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:store_websitetheme_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose the website theme')
        self.assertContains(response, 'Dark')
        self.assertContains(response, 'White')
        self.assertContains(response, 'Pink')

    def test_admin_can_switch_theme_directly_from_changelist(self):
        admin_user = User.objects.create_superuser('theme-switch-admin', 'themes@example.com', 'StrongPass!42')
        self.client.force_login(admin_user)
        WebsiteTheme.objects.create(theme='white')

        response = self.client.post(reverse('admin:store_websitetheme_set_theme', args=('pink',)))

        self.assertRedirects(response, reverse('admin:store_websitetheme_changelist'))
        self.assertEqual(WebsiteTheme.active_theme(), 'pink')
