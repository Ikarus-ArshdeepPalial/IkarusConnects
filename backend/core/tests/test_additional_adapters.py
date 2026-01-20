from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CRMConfiguration
from core.services import BrokerService
from core.adapters.pipedrive_adapter import PipedriveAdapter
from core.adapters.dynamics_adapter import DynamicsAdapter
from core.canonical_model import Contact

User = get_user_model()

class AdditionalAdaptersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='add@test.com', username='adduser', password='password')
        
        # Pipedrive Config
        self.pd_config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='pipedrive',
            # Mock mode: api_token is None or incomplete
            auth_config={'api_token': None}, 
            field_mapping={'name': 'name', 'email': 'email'}
        )
        
        # Dynamics Config
        self.dyn_config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='dynamics',
            # Mock mode: missing client_id/secret
            auth_config={'resource_url': 'https://org.crm.dynamics.com', 'client_id': None},
            field_mapping={'lastname': 'lastname'}
        )

    def test_pipedrive_mock_push(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'pipedrive')
        self.assertIsInstance(adapter, PipedriveAdapter)
        
        contact = Contact(first_name="Pipe", last_name="Drive")
        res = adapter.push_contact(contact)
        self.assertEqual(res, "MOCK_PD_ID_456")

    def test_dynamics_mock_push(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'dynamics')
        self.assertIsInstance(adapter, DynamicsAdapter)
        
        contact = Contact(last_name="DynamicsUser")
        res = adapter.push_contact(contact)
        self.assertEqual(res, "MOCK_DYN_GUID_123")

    def test_pipedrive_dynamic_target(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'pipedrive')
        contact = Contact(first_name="Custom", last_name="Endpoint")
        # Target = organizations
        res = adapter.push_contact(contact, target="organizations")
        self.assertEqual(res, "MOCK_PD_ID_456") # Mock return is static, but confirms no crash

    def test_dynamics_dynamic_target(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'dynamics')
        contact = Contact(last_name="Leads")
        # Target = leads
        res = adapter.push_contact(contact, target="leads")
        self.assertEqual(res, "MOCK_DYN_GUID_123")
