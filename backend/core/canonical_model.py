from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UnifiedEntity(BaseModel):
    """Base class for all unified entities."""
    id: Optional[str] = Field(None, description="The ID of the entity in the source CRM")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Original raw data from CRM")

class Contact(UnifiedEntity):
    """Unified representation of a Contact person."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Additional dynamic fields")

    def __init__(self, **data):
        # Extract known fields
        known_fields = {
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'company_name', 'job_title',
            'raw_data', 'created_at', 'updated_at'
        }
        
        # Everything else goes into custom_fields
        custom_fields = data.get('custom_fields', {})
        for key, value in data.items():
            if key not in known_fields and key != 'custom_fields':
                custom_fields[key] = value
        
        super().__init__(
            id=data.get('id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            company_name=data.get('company_name'),
            job_title=data.get('job_title'),
            custom_fields=custom_fields,
            raw_data=data.get('raw_data')
        )

class Lead(UnifiedEntity):
    """Unified representation of a Sales Lead."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    source: Optional[str] = None
    score: Optional[float] = None
