from rest_framework import views, status, permissions
from rest_framework.response import Response
from .serializers import CRMConfigurationSerializer, ContactSerializer
from core.models import CRMConfiguration
from core.services import BrokerService
import logging
import requests

logger = logging.getLogger(__name__)

class CRMConfigurationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        configs = CRMConfiguration.objects.filter(user=request.user)
        serializer = CRMConfigurationSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CRMConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SyncContactView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, crm_type):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.to_canonical()
            try:
                adapter = BrokerService.get_adapter_for_user(request.user, crm_type)
                # Pass data (Adapter handles target from its own config)
                result_id = adapter.push_contact(contact)
                return Response({
                    "status": "success",
                    "crm": crm_type,
                    "remote_id": result_id
                })
            except ValueError as e:
                # Configuration or Data Missing errors (e.g. missing fields)
                return Response({
                    "status": "error", 
                    "error_code": "CONFIGURATION_ERROR",
                    "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            except requests.exceptions.RequestException as e:
                # Upstream API Errors (HubSpot/Monday HTTP errors)
                error_details = str(e)
                if e.response is not None:
                    try:
                        # Try to parse JSON response from CRM
                        error_details = e.response.json()
                    except ValueError:
                        error_details = e.response.text
                
                return Response({
                    "status": "error",
                    "error_code": "CRM_API_ERROR", 
                    "message": "The CRM rejected the request.",
                    "details": error_details
                }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Catch-all for other errors (Salesforce, etc.)
                # We return 400 because it's usually due to bad input/config
                logger.error(f"Sync failed: {e}")
                return Response({
                    "status": "error",
                    "error_code": "SYNC_FAILED",
                    "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
