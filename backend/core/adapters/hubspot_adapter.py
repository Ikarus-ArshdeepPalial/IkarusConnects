from typing import List, Dict, Any
import requests
from .base_adapter import BaseAdapter
from ..canonical_model import Contact

class HubSpotAdapter(BaseAdapter):
    """
    Adapter for HubSpot CRM (API v3).
    """
    API_BASE_URL = "https://api.hubapi.com/crm/v3/objects"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = config.get("access_token")
        self.object_type = config.get("object_type")
        self.field_mapping = config.get("field_mapping", {})

    def authenticate(self) -> bool:
        if not self.access_token:
            print("HubSpot credentials incomplete. Running in MOCK mode.")
            return False
        # Logic to verify token could go here (e.g. hitting an endpoint)
        return True

    def fetch_contacts(self) -> List[Contact]:
        if not self.access_token:
            return [Contact(id="MOCK_HS_1", first_name="HubSpot", last_name="User", email="hubspot@test.com")]
        
        # Implementation skipped for now
        return []

    def push_contact(self, contact: Contact, target: str = None) -> str:
        # Determine Object Type: Argument (Priority) > Config (Priority 2)
        object_type = target if target else self.object_type
        if not object_type:
             raise ValueError("HubSpot Object Type not provided in Configuration.")
        
        # Prepare Properties
        properties = {}
        
        # Flatten contact data
        flat_contact = contact.model_dump()
        flat_contact.update(contact.custom_fields)
        
        # Strict Mapping: Only use mapped fields
        for key, value in flat_contact.items():
            if key in ['id', 'created_at', 'updated_at', 'raw_data', 'custom_fields']:
                continue 

            if key in self.field_mapping:
                hs_field = self.field_mapping[key]
                properties[hs_field] = value
        
        if not properties:
            raise ValueError("No fields mapped for HubSpot push. Please check 'field_mapping'.")

        if not self.access_token:
            print(f"[MOCK] Pushing to HubSpot ({object_type}): {properties}")
            return "MOCK_HS_ID_123"

        url = f"{self.API_BASE_URL}/{object_type}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json={"properties": properties}, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['id']
            
        except requests.exceptions.HTTPError as e:
            print(f"HubSpot API Error: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error creating HubSpot Object: {e}")
            raise
