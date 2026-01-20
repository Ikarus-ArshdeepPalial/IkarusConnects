from rest_framework import serializers
from core.models import CRMConfiguration
from core.canonical_model import Contact

class CRMConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMConfiguration
        fields = ['id', 'crm_type', 'api_url', 'auth_config', 'field_mapping' ,'created_at', 'updated_at']
        extra_kwargs = {'auth_config': {'write_only': True}} # Consider security for read

class ContactSerializer(serializers.Serializer):
    """
    Serializer for incoming Contact data to sync.
    Accepts any fields.
    """
    
    def to_internal_value(self, data):
        # Pass raw JSON straight through
        return data

    def to_representation(self, instance):
        return instance.model_dump()

    def to_canonical(self) -> Contact:
        # self.validated_data is the raw dict from to_internal_value
        return Contact(**self.validated_data)
