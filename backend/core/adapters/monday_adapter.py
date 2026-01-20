from typing import List, Dict, Any
import requests
from .base_adapter import BaseAdapter
from ..canonical_model import Contact

class MondayAdapter(BaseAdapter):
    """
    Adapter for Monday.com (GraphQL API).
    """
    API_URL = "https://api.monday.com/v2"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_token = config.get("api_token")
        self.board_id = config.get("board_id")
        self.field_mapping = config.get("field_mapping", {})

    def authenticate(self) -> bool:
        if not self.api_token or not self.board_id:
            print("Monday.com credentials incomplete. Running in MOCK mode.")
            return False
        # Basic check to see if token is valid (optional, e.g. query users)
        return True

    def fetch_contacts(self) -> List[Contact]:
        if not self.api_token:
            return [Contact(id="MOCK_MON_1", first_name="Monday", last_name="User", email="monday@test.com")]
        
        # Implementation for fetch skipped for now as we focus on push
        return []

    def push_contact(self, contact: Contact, target: str = None) -> str:
        # 1. Prepare Column Values
        import json
        
        # Determine Board ID: Argument (Priority) > Config
        target_board_id = target if target else self.board_id
        if not target_board_id:
             raise ValueError("Monday Board ID not provided in URL or Config.")

        column_values = {}
        
        # Flatten contact data
        flat_contact = contact.model_dump()
        flat_contact.update(contact.custom_fields)
        
        # Logic: Find which field is mapped to "Name"
        name_field_key = None
        for key, monday_col in self.field_mapping.items():
            if monday_col == "Name":
                name_field_key = key
                break
        
        # If we found a key mapped to "Name", use its value
        item_name = None
        if name_field_key and name_field_key in flat_contact:
            item_name = flat_contact[name_field_key]
        
        if not item_name:
             raise ValueError("Monday Item Name ('Name') not mapped in configuration.")
        
        # Map everything else
        for key, value in flat_contact.items():
            if key == name_field_key: 
                continue # Already used for Item Name
            
            if key in ['id', 'created_at', 'updated_at', 'raw_data', 'custom_fields']:
                continue

            if key in self.field_mapping:
                monday_col_id = self.field_mapping[key]
                column_values[monday_col_id] = value

        if not self.api_token:
            print(f"[MOCK] Pushing to Monday Board {target_board_id}: {item_name}, Cols: {column_values}")
            return "MOCK_MON_ITEM_123"

        # 2. GraphQL Mutation
        query = """
        mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
            create_item (board_id: $board_id, item_name: $item_name, column_values: $column_values) {
                id
            }
        }
        """
        
        variables = {
            "board_id": int(target_board_id),
            "item_name": item_name,
            "column_values": json.dumps(column_values)
        }
        
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.API_URL, 
                json={'query': query, 'variables': variables}, 
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise Exception(f"Monday API Errors: {data['errors']}")
                
            return data['data']['create_item']['id']
            
        except Exception as e:
            print(f"Error creating Monday Item: {e}")
            raise
