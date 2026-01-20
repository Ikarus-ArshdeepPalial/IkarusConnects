from django.urls import path
from .views import CRMConfigurationView, SyncContactView

urlpatterns = [
    path('config/', CRMConfigurationView.as_view(), name='crm-config'),
    path('sync/<str:crm_type>/', SyncContactView.as_view(), name='sync-contact'),
]
