from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import CRMConfiguration
from core.canonical_model import Contact

User = get_user_model()

class UserIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = '/api/user/signup/'
        self.login_url = '/api/user/login/'
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123',
            'name': 'Test User'
        }

    def test_full_user_flow(self):
        # 1. Signup
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Login to get Token
        login_data = {'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        token = response.data['access']
        
        # 3. Authenticated Request to CRM Config
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Add Config
        config_data = {
            'crm_type': 'salesforce',
            'auth_config': {'username': 'mock'},
            'field_mapping': {'job': 'Title'}
        }
        res = self.client.post('/api/config/', config_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # 4. Sync Data using JWT
        sync_payload = {
            'first_name': 'JWT', 
            'last_name': 'User', 
            'email': 'jwt@test.com',
            'custom_fields': {'job': 'Developer'}
        }
        res = self.client.post('/api/sync/salesforce/contact/', sync_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'success')

