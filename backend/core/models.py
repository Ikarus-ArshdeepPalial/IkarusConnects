from django.db import models
from django.conf import settings

class CRMConfiguration(models.Model):
    CRM_CHOICES = [
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('zoho', 'Zoho CRM'),
        ('monday', 'Monday.com'),
        ('pipedrive', 'Pipedrive'),
        ('dynamics', 'Microsoft Dynamics 365'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crm_configurations')
    crm_type = models.CharField(max_length=50, choices=CRM_CHOICES)
    api_url = models.URLField(help_text="Base API URL for the CRM", blank=True, null=True)
    
    # Storing credentials as JSON. In production, this should be encrypted.
    auth_config = models.JSONField(help_text="JSON containing client_id, client_secret, tokens, etc.")
    field_mapping = models.JSONField(default=dict, blank=True, help_text="Mapping from JSON keys to CRM specific fields. E.g. {'website_field': 'CRM_Field'}")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'crm_type')

    def __str__(self):
        return f"{self.user.username} - {self.crm_type}"
