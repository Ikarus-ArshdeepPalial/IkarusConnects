from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CRMConfiguration
from core.services import BrokerService
from core.adapters.monday_adapter import MondayAdapter
from core.canonical_model import Contact

User = get_user_model()

class MondayAdapterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='monday@test.com', username='mondayuser', password='password')
        self.config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='monday',
            auth_config={'api_token': None, 'board_id': '12345'}, # Mock mode
            field_mapping={'email': 'email_col', 'job': 'job_col'}
        )

    def test_adapter_instantiation(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'monday')
        self.assertIsInstance(adapter, MondayAdapter)

    def test_adapter_push_mock(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'monday')
        contact = Contact(
            first_name="Monday", 
            last_name="Test", 
            email="test@monday.com",
            custom_fields={"job": "Dev"}
        )
        
        # Test that it captures mapping correctly even in mock
        res_id = adapter.push_contact(contact)
        self.assertTrue(res_id.startswith("MOCK_MON"))
