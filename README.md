# IkarusConnects

The definitive guide to connecting your business data. Ikarus Connects is a universal connector that bridges your business logic with various CRM platforms, enabling seamless data synchronization.

## Features

-   **Unified API**: Connect to multiple CRMs through a single interface.
-   **Supported Integrations**:
    -   Salesforce
    -   HubSpot
    -   Monday.com
    -   Pipedrive
    -   Microsoft Dynamics 365
-   **Secure Authentication**: User management with JWT support.
-   **Configurable**: Dynamic configuration for different CRM types.

## Tech Stack

-   Python
-   Django & Django REST Framework
-   Celery (for background tasks)
-   PostgreSQL / SQLite

---

## Getting Started

### Prerequisites

-   Python 3.10+
-   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd universal_connector
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

4.  **Start the Server:**
    ```bash
    python manage.py runserver
    ```

---

## Authentication

To use the API, you must first create an account and obtain an authentication token.

### 1. Sign Up

**Endpoint:** `POST /api/user/Signup/`

**Payload:**
```json
{
  "username": "YOUR_USERNAME",
  "email": "YOUR_EMAIL",
  "password": "YOUR_PASSWORD",
  "confirm_password": "CONFIRM_PASSWORD"
}
```

### 2. Login

**Endpoint:** `POST /api/user/login/`

**Payload:**
```json
{
  "email": "YOUR_EMAIL",
  "password": "YOUR_PASSWORD"
}
```

**Response:** You will receive an access token. Include this token in the Authorization header for subsequent requests.

---

## Configuration

Before syncing data, you need to configure your CRM connection. This is a one-time setup per CRM instance.

**Endpoint:** `POST /api/config/`

### 1. Salesforce Integration

Connect using a Secure Connected App.

**Setup Guide:**
1.  **Login** to Salesforce.
2.  Navigate to **Setup** → **External Client Apps** → **Settings**.
3.  Enable **Connected Apps**.
4.  Click **New Connected App**. Name it "Universal Connector".
5.  **OAuth Config**: Enable OAuth Settings.
    *   **Callback URL**: `http://localhost:8000/callback`
    *   **Scopes**: Add `Manage user data via APIs (api)` and `Perform requests on your behalf at any time (refresh_token, offline_access)`.
6.  **Secrets**: Save and copy your **Key** (client_id) and **Secret** (client_secret).
7.  **Flows**: In OAuth and OpenId Connect Settings, enable **Allow OAuth Username-Password Flows**.

**Payload:**
```json
{
  "crm_type": "salesforce",
  "auth_config": {
    "username": "YOUR_SALESFORCE_USERNAME",
    "password": "YOUR_SALESFORCE_PASSWORD",
    "security_token": "YOUR_SECURITY_TOKEN",
    "client_id": "YOUR_CONSUMER_KEY",
    "client_secret": "YOUR_CONSUMER_SECRET",
    "Object_name": "Ikarus_Customer__c"
  },
  "field_mapping": {}
}
```

### 2. HubSpot Integration

Sync contacts and deals using a Private App.

**Setup Guide:**
1.  Go to **Settings** → **Integrations** → **Private Apps**.
2.  Click **Create a private app** and name it "Universal Connector".
3.  **Define Scopes**:
    *   `crm.objects.contacts` (Read/Write)
    *   `crm.objects.companies` (Read/Write)
    *   `crm.objects.deals` (Read/Write)
    *   `crm.schemas.custom` (Read/Write)
4.  **Token**: Click **Create App** and copy the **Access Token**.

**Payload:**
```json
{
  "crm_type": "hubspot",
  "auth_config": {
    "api_token": "YOUR_ACCESS_TOKEN",
    "object_type": "PAGE"
  },
  "field_mapping": {}
}
```

### 3. Monday.com Integration

Connect boards and manage items.

**Setup Guide:**
1.  Go to your **Admin Section**.
2.  Generate your **Personal API Token**.
3.  Create a board and get the **Board ID** from the URL.

**Payload:**
```json
{
  "crm_type": "monday",
  "auth_config": {
    "api_token": "YOUR_API_TOKEN",
    "board_id": "YOUR_BOARD_ID"
  },
  "field_mapping": {}
}
```

### 4. Pipedrive Integration

Bridge Pipedrive deals into your workflow.

**Setup Guide:**
1.  Click your **User Icon** → **Personal preferences**.
2.  Go to the **API** tab.
3.  Generate or copy your **Personal API token**.

**Payload:**
```json
{
  "crm_type": "pipedrive",
  "auth_config": {
    "api_token": "YOUR_PERSONAL_TOKEN",
    "object_type": "DEAL"
  },
  "field_mapping": {}
}
```

### 5. Microsoft Dynamics 365 Integration

Sync using Azure App Registrations and Service Accounts.

**Payload:**
```json
{
  "crm_type": "dynamics",
  "auth_config": {
    "resource_url": "https://org.crm.dynamics.com",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "tenant_id": "YOUR_TENANT_ID"
  },
  "field_mapping": {}
}
```

---

## Usage

Once configured, you can sync data by making a request to the sync endpoint.

**Endpoint:** `POST /api/sync/<name_of_crm>/`

**Example Payload:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "product_name": "Laptop"
}
```
*Note: The payload fields should match your configured field mappings or the expected schema of the target CRM object.*
