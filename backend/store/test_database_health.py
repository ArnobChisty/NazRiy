from django.test import TestCase


class DatabaseHealthTests(TestCase):
    def test_health_endpoint_confirms_database_connection(self):
        response = self.client.get('/api/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['database'], 'postgresql')
        self.assertIn(response.data['media_storage'], {'local', 'supabase'})
