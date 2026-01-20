from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CRMConfiguration
from core.services import BrokerService
from core.adapters.hubspot_adapter import HubSpotAdapter
from core.canonical_model import Contact

User = get_user_model()

class HubSpotAdapterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='hubspot@test.com', username='hubspotuser', password='password')
        self.config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='hubspot',
            auth_config={'access_token': None, 'object_type': 'contacts'}, # Mock
            field_mapping={'email': 'email', 'firstname': 'firstname'}
        )

    def test_adapter_instantiation(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'hubspot')
        self.assertIsInstance(adapter, HubSpotAdapter)

    def test_push_mock_default(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'hubspot')
        contact = Contact(first_name="Hub", last_name="Spot", email="test@hubspot.com")
        res = adapter.push_contact(contact)
        self.assertEqual(res, "MOCK_HS_ID_123")

    def test_push_mock_override(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'hubspot')
        contact = Contact(first_name="Hub", last_name="Spot", email="test@hubspot.com")
        # Target custom object
        res = adapter.push_contact(contact, target="deals")
        # In mock mode it just returns ID, but we verify it runs
        self.assertEqual(res, "MOCK_HS_ID_123")
        
    def test_strict_mapping_error(self):
        # Create config with NO mapping
        self.config.field_mapping = {}
        self.config.save()
        
        adapter = BrokerService.get_adapter_for_user(self.user, 'hubspot')
        contact = Contact(email="nomap@test.com")
        
        with self.assertRaises(ValueError) as context:
            adapter.push_contact(contact)
        self.assertIn("No fields mapped", str(context.exception))
