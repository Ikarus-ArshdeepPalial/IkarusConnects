from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..canonical_model import Contact

class BaseAdapter(ABC):
    """
    Abstract base class for all CRM adapters.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with configuration dictionary (from CRMConfiguration.auth_config).
        """
        self.config = config

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticates with the CRM.
        """
        pass

    @abstractmethod
    def fetch_contacts(self) -> List[Contact]:
        """
        Fetches contacts from the CRM.
        """
        pass

    @abstractmethod
    def push_contact(self, contact: Contact, target: str = None) -> str:
        """
        Pushes a unified Contact to the CRM.
        :param contact: The unified contact object.
        :param target: Optional target entity (e.g. Board ID, Object Name).
        :return: The ID of the created/updated record in the CRM.
        """
        pass
