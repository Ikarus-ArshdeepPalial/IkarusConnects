from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import CRMConfiguration

User = get_user_model()

class APITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='api@test.com', username='apiuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        CRMConfiguration.objects.create(
            user=self.user,
            crm_type='salesforce',
            auth_config={'username': None}
        )

    def test_sync_endpoint(self):
        payload = {
            "first_name": "API",
            "last_name": "Test",
            "email": "api@test.com"
        }
        response = self.client.post('/api/sync/salesforce/contact/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['crm'], 'salesforce')

    def test_config_retrieval(self):
        response = self.client.get('/api/config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['crm_type'], 'salesforce')
