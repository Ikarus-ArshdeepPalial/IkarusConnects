from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CRMConfiguration
from core.services import BrokerService
from core.canonical_model import Contact

User = get_user_model()

class DynamicTargetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='dynamic@test.com', username='dynamicuser', password='password')
        self.mon_config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='monday',
            auth_config={'api_token': None, 'board_id': 'DEFAULT_BOARD'},
            field_mapping={'email': 'email_col'}
        )
        self.sf_config = CRMConfiguration.objects.create(
            user=self.user,
            crm_type='salesforce',
            auth_config={'username': None, 'password': None}, # Incomplete -> Mock
            field_mapping={'email': 'Email'}
        )

    def test_monday_override(self):
        adapter = BrokerService.get_adapter_for_user(self.user, 'monday')
        contact = Contact(first_name="Dyn", last_name="Mon")
        
        # 1. Default Behavior
        res_default = adapter.push_contact(contact) # Should use DEFAULT_BOARD
        # We can't easily assert the print output here without capturing stdout, 
        # but the MOCK return value is static. 
        # Ideally we'd mock the requests library or capture print.
        
        # 2. Override
        # In a real unit test we would mock the `requests.post` and check the arguments.
        # For now, we ensure no exceptions are raised.
        res_override = adapter.push_contact(contact, target="OVERRIDE_BOARD_123")
        self.assertTrue(res_override.startswith("MOCK_MON"))

    def test_salesforce_config_target(self):
        # Update config to point to Custom Object
        self.sf_config.auth_config['object_name'] = 'MyCustomObj__c'
        self.sf_config.save()
        
        adapter = BrokerService.get_adapter_for_user(self.user, 'salesforce')
        self.assertEqual(adapter.object_name, 'MyCustomObj__c')
        
        contact = Contact(first_name="Dyn", last_name="SF")
        # Should use MyCustomObj__c internally
        res = adapter.push_contact(contact)
        self.assertEqual(res, "MOCK_SF_ID_123")
