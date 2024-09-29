# standard library imports
import requests
import os

# third party imports
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# local imports
from app.config import Config
from app.schem import UserSignup, UserLogin, ChangePassword, EditProfile

class AuthService:
    @staticmethod
    def get_access_token():
        payload = {
            'grant_type': 'client_credentials',
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default'
        }
        AUTH_URL =f'https://{os.getenv("TENANT_ID")}.b2clogin.com/{os.getenv("TENANT_ID")}.onmicrosoft.com/oauth2/v2.0/token'
        response = requests.post(Config.AUTH_URL, data=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json().get('access_token')

    @staticmethod
    def signup(user: UserSignup):
        token = AuthService.get_access_token()
        user_payload = {
            "accountEnabled": True,
            "displayName": user.username,
            "mailNickname": user.username.split('@')[0],
            "userPrincipalName": f"{user.username}",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": False,
                "password": user.password
            }
        }
        response = requests.post(
            f"{Config.GRAPH_API_URL}/users",
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=user_payload
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

    @staticmethod
    def login(user: UserLogin):
        payload = {
            'grant_type': 'password',
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'scope': 'openid',
            'username': user.username,
            'password': user.password
        }
        response = requests.post(Config.AUTH_URL, data=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

    @staticmethod
    def change_password(data: ChangePassword):
        token = AuthService.get_access_token()
        change_password_payload = {
            "passwordProfile": {
                "password": data.new_password,
                "forceChangePasswordNextSignIn": False
            }
        }
        response = requests.patch(
            f"{Config.GRAPH_API_URL}/users/{data.username}",
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=change_password_payload
        )
        if response.status_code != 204:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return {"detail": "Password changed successfully"}

    @staticmethod
    def edit_profile(data: EditProfile):
        token = AuthService.get_access_token()
        edit_profile_payload = {
            "displayName": data.display_name
        }
        response = requests.patch(
            f"{Config.GRAPH_API_URL}/users/{data.username}",
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=edit_profile_payload
        )
        if response.status_code != 204:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return {"detail": "Profile updated successfully"}
