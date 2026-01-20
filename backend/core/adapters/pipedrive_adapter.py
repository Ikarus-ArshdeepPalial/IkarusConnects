from typing import List, Dict, Any
import requests
from .base_adapter import BaseAdapter
from ..canonical_model import Contact

class PipedriveAdapter(BaseAdapter):
    """
    Adapter for Pipedrive CRM (REST API v1).
    Auth: API Token via Query Parameter.
    """
    API_BASE_URL = "https://api.pipedrive.com/v1"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_token = config.get("api_token")
        self.object_type = config.get("object_type") # e.g. 'persons', 'deals'
        self.field_mapping = config.get("field_mapping", {})

    def authenticate(self) -> bool:
        if not self.api_token:
            print("[Mock] Pipedrive credentials incomplete.")
            return False
        return True

    def fetch_contacts(self) -> List[Contact]:
        return []

    def push_contact(self, contact: Contact, target: str = None) -> str:
        # Pipedrive typically calls contacts 'persons'
        endpoint = target if target else self.object_type
        if not endpoint:
             raise ValueError("Pipedrive Object Type (e.g. 'persons') not provided in keys.")
        
        if not self.api_token:
            print(f"[MOCK] Pushing to Pipedrive ({endpoint}).")
            return "MOCK_PD_ID_456"

        payload = {}
        
        # Flatten contact data
        flat_contact = contact.model_dump()
        flat_contact.update(contact.custom_fields)
        
        # Strict mapping required
        for key, value in flat_contact.items():
             if key in self.field_mapping:
                 pd_field = self.field_mapping[key]
                 payload[pd_field] = value
        
        if not payload:
            raise ValueError("No fields mapped for Pipedrive.")

        # Pipedrive requires name if creating a person, but we rely on mapping.
        # API Token is passed as query param 'api_token'
        url = f"{self.API_BASE_URL}/{endpoint}"
        params = {"api_token": self.api_token}
        
        try:
            response = requests.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            # Pipedrive response structure: { "success": true, "data": { "id": 123, ... } }
            return str(data.get('data', {}).get('id', 'UNKNOWN'))
            
        except requests.exceptions.HTTPError as e:
            print(f"Pipedrive API Error: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error creating Pipedrive Record: {e}")
            raise
