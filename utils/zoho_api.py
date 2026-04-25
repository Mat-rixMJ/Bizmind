import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ZohoClient:
    def __init__(self):
        self.org_id = os.getenv('ZOHO_ORG_ID')
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.access_token = None
        self.base_url = "https://www.zohoapis.com/books/v3"

    def refresh_access_token(self):
        """Refreshes the OAuth2 access token using the refresh token."""
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            return True
        return False

    def get_headers(self):
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "X-com-zoho-invoice-organizationid": self.org_id
        }

    def fetch_items(self):
        """Fetches items (Inventory) from Zoho Books."""
        if not self.access_token and not self.refresh_access_token():
            return None
        
        url = f"{self.base_url}/items"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            return response.json().get("items", [])
        return None

    def fetch_invoices(self):
        """Fetches invoices (Transactions) from Zoho Books."""
        if not self.access_token and not self.refresh_access_token():
            return None
        
        url = f"{self.base_url}/invoices"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            return response.json().get("invoices", [])
        return None
