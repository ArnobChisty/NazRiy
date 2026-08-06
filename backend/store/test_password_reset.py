import re
from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_URL='https://shop.example.com',
    PASSWORD_RESET_TIMEOUT=3600,
)
class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reset-buyer',
            email='buyer@example.com',
            password='OriginalStrong!42',
            first_name='NazRiy',
        )

    def request_reset(self, email='buyer@example.com'):
        return self.client.post('/api/auth/password/reset/', {'email': email}, format='json')

    def reset_credentials(self):
        response = self.request_reset()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r'reset-password\?uid=([^&\s]+)&token=([^\s<]+)', mail.outbox[0].body)
        self.assertIsNotNone(match)
        return match.group(1), match.group(2)

    def test_request_is_enumeration_safe_and_sends_professional_email(self):
        known = self.request_reset()
        unknown = self.request_reset('missing@example.com')

        self.assertEqual(known.status_code, 200)
        self.assertEqual(unknown.status_code, 200)
        self.assertEqual(known.data, unknown.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reset your NazRiy password')
        self.assertIn('https://shop.example.com/reset-password?uid=', mail.outbox[0].body)
        self.assertTrue(mail.outbox[0].alternatives)

    def test_token_can_be_checked_and_used_only_once(self):
        uid, token = self.reset_credentials()
        validation = self.client.get('/api/auth/password/reset/confirm/', {'uid': uid, 'token': token})
        self.assertEqual(validation.status_code, 200)
        self.assertTrue(validation.data['valid'])

        changed = self.client.post('/api/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'ReplacementStrong!42',
            'confirm_password': 'ReplacementStrong!42',
        }, format='json')
        self.assertEqual(changed.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ReplacementStrong!42'))
        self.assertFalse(self.user.check_password('OriginalStrong!42'))

        reused = self.client.post('/api/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'AnotherReplacement!42',
            'confirm_password': 'AnotherReplacement!42',
        }, format='json')
        self.assertEqual(reused.status_code, 400)

    def test_invalid_mismatched_and_weak_passwords_are_rejected(self):
        uid, token = self.reset_credentials()
        invalid = self.client.get('/api/auth/password/reset/confirm/', {'uid': uid, 'token': 'invalid'})
        self.assertEqual(invalid.status_code, 400)

        mismatch = self.client.post('/api/auth/password/reset/confirm/', {
            'uid': uid, 'token': token, 'new_password': 'ReplacementStrong!42', 'confirm_password': 'different',
        }, format='json')
        self.assertEqual(mismatch.status_code, 400)
        self.assertIn('confirm_password', mismatch.data)

        weak = self.client.post('/api/auth/password/reset/confirm/', {
            'uid': uid, 'token': token, 'new_password': 'password', 'confirm_password': 'password',
        }, format='json')
        self.assertEqual(weak.status_code, 400)
        self.assertIn('new_password', weak.data)

    def test_token_expires_after_configured_timeout(self):
        issued_at = datetime.now()
        with patch('django.contrib.auth.tokens.PasswordResetTokenGenerator._now', return_value=issued_at):
            uid, token = self.reset_credentials()

        with patch(
            'django.contrib.auth.tokens.PasswordResetTokenGenerator._now',
            return_value=issued_at + timedelta(seconds=3601),
        ):
            expired = self.client.get('/api/auth/password/reset/confirm/', {'uid': uid, 'token': token})

        self.assertEqual(expired.status_code, 400)
        self.assertFalse(expired.data['valid'])
