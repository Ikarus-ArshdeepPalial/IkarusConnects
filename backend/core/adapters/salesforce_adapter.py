from typing import List, Dict, Any
from simple_salesforce import Salesforce
from .base_adapter import BaseAdapter
from ..canonical_model import Contact

class SalesforceAdapter(BaseAdapter):
    """
    Adapter for Salesforce CRM.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.username = config.get("username")
        self.password = config.get("password")
        self.security_token = config.get("security_token", "")
        self.session_id = config.get("session_id")
        self.instance_url = config.get("instance_url")
        # OAuth Credentials
        self.client_id = config.get("client_id") # consumer_key
        self.client_secret = config.get("client_secret") # consumer_secret
        
        self.object_name = config.get("object_name")
        self.domain = config.get("domain", "login")
        self.client = None

    def authenticate(self) -> bool:
        try:
            if self.session_id and self.instance_url:
                # Legacy: Session ID
                self.client = Salesforce(
                    instance_url=self.instance_url,
                    session_id=self.session_id
                )
            elif self.username and self.password and self.client_id and self.client_secret:
                # OAuth: Username-Password Flow (REST API)
                import requests
                
                # Determine Login URL (Test vs Prod)
                login_domain = self.domain if self.domain else "login"
                if "test" in (self.instance_url or ""):
                    login_domain = "test"
                
                token_url = f"https://{login_domain}.salesforce.com/services/oauth2/token"
                
                payload = {
                    'grant_type': 'password',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'username': self.username,
                    'password': f"{self.password}{self.security_token}"
                }
                
                response = requests.post(token_url, data=payload)
                if response.status_code != 200:
                    raise Exception(f"OAuth Error: {response.text}")
                
                data = response.json()
                self.client = Salesforce(
                    instance_url=data['instance_url'],
                    session_id=data['access_token']
                )
            else:
                print("[Mock] Salesforce credentials incomplete.")
                return False
                
            return True
        except Exception as e:
            print(f"Salesforce Auth Failed: {e}")
            raise

    def fetch_contacts(self) -> List[Contact]:
        if not self.client:
            # Mock Data
            return [
                Contact(id="MOCK_SF_1", first_name="Django", last_name="User", email="django@test.com")
            ]

        query = "SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT 10"
        results = self.client.query(query)
        
        contacts = []
        for record in results['records']:
            contacts.append(Contact(
                id=record['Id'],
                first_name=record['FirstName'],
                last_name=record['LastName'],
                email=record['Email'],
                phone=record['Phone'],
                raw_data=record
            ))
        return contacts

    def push_contact(self, contact: Contact, target: str = None) -> str:
        # Determine Salesforce Object: Argument (Priority) > Config (Priority 2)
        sobject_name = target if target else self.object_name
        if not sobject_name:
             raise ValueError("Salesforce Object Name not provided in URL or Config.")
        
        # Build payload dynamically
        sf_contact = {}
        
        # Flatten contact data
        flat_contact = contact.model_dump()
        flat_contact.update(contact.custom_fields)

        # Logic: Find which field is mapped to "LastName" (Required by Salesforce Contacts/Leads)
        field_mapping = self.config.get('field_mapping', {})
        lastname_key = None
        for key, crm_field in field_mapping.items():
            if crm_field == "LastName":
                lastname_key = key
                break
        
        # Resolve LastName (Strictly for Contact/Lead) or Generic Name Mappings
        if lastname_key and lastname_key in flat_contact:
             sf_contact['LastName'] = flat_contact[lastname_key]
        elif sobject_name in ['Contact', 'Lead']:
            # For Standard Objects, LastName is mandatory
            if contact.last_name:
                sf_contact['LastName'] = contact.last_name
            else:
                 sf_contact['LastName'] = "Unknown"

        # Resolve First Name (Optional but good to have)
        if contact.first_name:
            sf_contact['FirstName'] = contact.first_name

        # Map everything else
        for key, value in flat_contact.items():
            if key == lastname_key: 
                continue 
            
            if key in ['id', 'created_at', 'updated_at', 'raw_data', 'custom_fields', 'first_name', 'last_name']:
                continue

            if key in field_mapping:
                crm_field = field_mapping[key]
                sf_contact[crm_field] = value
                
        if not self.client:
            print(f"[MOCK] Pushing to Salesforce: {sf_contact}")
            return "MOCK_SF_ID_123"

        try:
            # Dynamic Object Creation using getattr
            sobject = getattr(self.client, sobject_name)
            result = sobject.create(sf_contact)
            return result['id']
        except Exception as e:
            print(f"Error creating Salesforce Contact: {e}")
            raise
