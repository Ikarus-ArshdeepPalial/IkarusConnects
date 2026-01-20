from django.contrib.auth import get_user_model
from django.conf import settings
from .models import CRMConfiguration
from .adapters.base_adapter import BaseAdapter
from .adapters.salesforce_adapter import SalesforceAdapter
from .adapters.monday_adapter import MondayAdapter
from .adapters.hubspot_adapter import HubSpotAdapter
from .adapters.pipedrive_adapter import PipedriveAdapter
from .adapters.dynamics_adapter import DynamicsAdapter
from typing import Type

User = get_user_model()

class BrokerService:
    
    ADAPTER_MAP: dict[str, Type[BaseAdapter]] = {
        'salesforce': SalesforceAdapter,
        'monday': MondayAdapter,
        'hubspot': HubSpotAdapter,
        'pipedrive': PipedriveAdapter,
        'dynamics': DynamicsAdapter,
    }

    @classmethod
    def get_adapter_for_user(cls, user: settings.AUTH_USER_MODEL, crm_type: str) -> BaseAdapter:
        """
        Retrieves the CRM configuration for the user and instantiates the adapter.
        """
        print("here in get adapter")
        try:
            config_model = CRMConfiguration.objects.get(user=user, crm_type=crm_type)
        except CRMConfiguration.DoesNotExist:
            raise ValueError(f"No configuration found for {crm_type} for user {user.username}")
        
        adapter_class = cls.ADAPTER_MAP.get(crm_type)
        if not adapter_class:
            raise ValueError(f"No adapter implementation for {crm_type}")
        
        # Instantiate adapter with the stored config
        config = config_model.auth_config.copy()
        config['field_mapping'] = config_model.field_mapping
        adapter = adapter_class(config)
        adapter.authenticate()
        return adapter
