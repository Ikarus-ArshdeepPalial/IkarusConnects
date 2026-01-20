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
        self.sf = None
        self.username = config.get("username")
        self.password = config.get("password")
        self.security_token = config.get("security_token")
        self.domain = config.get("domain", "login")
        self.session_id = config.get("session_id")
        self.instance_url = config.get("instance_url")
        self.object_name = config.get("object_name")

    def authenticate(self) -> bool:
        try:
            # Priority 1: Session ID (Bypasses SOAP Login)
            if self.session_id and self.instance_url:
                self.sf = Salesforce(
                    instance_url=self.instance_url,
                    session_id=self.session_id
                )
                return True

            # Priority 2: Username/Password (SOAP Login)
            if not all([self.username, self.password, self.security_token]):
                print("Salesforce credentials incomplete. Running in MOCK mode.")
                return False

            self.sf = Salesforce(
                username=self.username, 
                password=self.password, 
                security_token=self.security_token,
                domain=self.domain
            )
            return True
        except Exception as e:
            print(f"Salesforce authentication failed: {e}")
            raise

    def fetch_contacts(self) -> List[Contact]:
        if not self.sf:
            # Mock Data
            return [
                Contact(id="MOCK_SF_1", first_name="Django", last_name="User", email="django@test.com")
            ]

        query = "SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT 10"
        results = self.sf.query(query)
        
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
                
        if not self.sf:
            print(f"[MOCK] Pushing to Salesforce: {sf_contact}")
            return "MOCK_SF_ID_123"

        try:
            # Dynamic Object Creation using getattr
            sobject = getattr(self.sf, sobject_name)
            result = sobject.create(sf_contact)
            return result['id']
        except Exception as e:
            print(f"Error creating Salesforce Contact: {e}")
            raise
