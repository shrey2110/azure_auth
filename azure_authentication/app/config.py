 # app/config.py

import os

class Config:
    TENANT_ID = os.getenv("TENANT_ID", "your_tenant_id")
    CLIENT_ID = os.getenv("CLIENT_ID", "your_client_id")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your_client_secret")
    AUTH_URL = f'https://login.microsoftonline.com/{os.getenv("TENANT_ID")}/oauth2/v2.0/token'
    GRAPH_API_URL = 'https://graph.microsoft.com/v1.0'
