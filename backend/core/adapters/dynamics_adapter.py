from typing import List, Dict, Any
import requests
from .base_adapter import BaseAdapter
from ..canonical_model import Contact

class DynamicsAdapter(BaseAdapter):
    """
    Adapter for Microsoft Dynamics 365 (Dataverse / Web API).
    Auth: OAuth 2.0 Client Credentials Flow (Server-to-Server).
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.tenant_id = config.get("tenant_id")
        self.resource_url = config.get("resource_url") # e.g. https://org12345.crm.dynamics.com
        self.object_type = config.get("object_type") # e.g. 'contacts', 'leads'
        self.field_mapping = config.get("field_mapping", {})
        self._access_token = None

    def _get_access_token(self) -> str:
        """
        Exchanges Client Credentials for a Bearer Token.
        """
        if self._access_token:
            return self._access_token
            
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": f"{self.resource_url}/.default"
        }
        
        resp = requests.post(token_url, data=data)
        resp.raise_for_status()
        self._access_token = resp.json().get("access_token")
        return self._access_token

    def authenticate(self) -> bool:
        if not (self.client_id and self.client_secret and self.tenant_id and self.resource_url):
            print("[Mock] Dynamics credentials incomplete.")
            return False
        # Ideally try to fetch token here to verify
        try:
            self._get_access_token()
            return True
        except Exception as e:
            print(f"Dynamics Auth Failed: {e}")
            return False

    def fetch_contacts(self) -> List[Contact]:
        return []

    def push_contact(self, contact: Contact, target: str = None) -> str:
        # Default target: 'contacts' (Entity Set Name)
        entity_set_name = target if target else self.object_type
        if not entity_set_name:
             raise ValueError("Dynamics Entity Set Name (e.g. 'contacts') not provided.")
        
        if not (self.client_id and self.client_secret):
             print(f"[MOCK] Pushing to Dynamics ({entity_set_name})")
             return "MOCK_DYN_GUID_123"

        # Prepare Payload
        payload = {}
        flat_contact = contact.model_dump()
        flat_contact.update(contact.custom_fields)
        
        for key, value in flat_contact.items():
            if key in self.field_mapping:
                dyn_field = self.field_mapping[key]
                payload[dyn_field] = value
                
        if not payload:
            raise ValueError("No fields mapped for Dynamics 365.")

        try:
            token = self._get_access_token()
            url = f"{self.resource_url.rstrip('/')}/api/data/v9.2/{entity_set_name}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Ask for created data back
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Dynamics returns the created entity with ID usually in 'contactid' or similar
            # If 'return=representation' is honored, we get JSON.
            # ID key often matches entity name + 'id', e.g. 'contactid', 'leadid'.
            # We will try to scan for an ID-like field if specific one isn't clear, 
            # or just return success if 201 Created.
            data = response.json()
            
            # Heuristic to find ID: usually e.g. contactid
            # Or use header 'OData-EntityId' if available
            if 'OData-EntityId' in response.headers:
                 return response.headers['OData-EntityId']
            
            # Return full data ID if found, otherwise generic success
            return str(data.get(f"{entity_set_name[:-1]}id", "CREATED"))

        except requests.exceptions.HTTPError as e:
            print(f"Dynamics API Error: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error creating Dynamics Record: {e}")
            raise
