# imports from standard library
import os
import httpx

# third party imports
from fastapi import FastAPI,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# local imports
from app.auth import AuthService
from app.schem import UserSignup, UserLogin, ChangePassword, EditProfile

# Initialize the FastAPI app
app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup")
async def signup(user: UserSignup):
    # Create user in Azure AD
    signup_url = f'https://graph.microsoft.com/v1.0/users'
    
    # Define the payload for creating the user
    payload = {
        "accountEnabled": True,
        "displayName": user.display_name,
        "mailNickname": user.username.split('@')[0],  # Mail nickname (usually the part before @)
        "creationType": "LocalAccount",  # e.g., user@example.com
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False,
            "password": user.password
        }
    }
    
    # Get an access token for Graph API
    token_url = f'https://login.microsoftonline.com/{os.getenv("TENANT_ID")}/oauth2/v2.0/token'
    token_payload = {
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET"),
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'  # Using client credentials for admin actions
    }

    async with httpx.AsyncClient() as client:
        # First, get the access token
        token_response = await client.post(token_url, data=token_payload)

        if token_response.status_code != 200:
            raise HTTPException(status_code=token_response.status_code, detail="Failed to get access token.")

        access_token = token_response.json().get("access_token")

        # Now create the user
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = await client.post(signup_url, headers=headers, json=payload)

        if response.status_code == 201:  # User created successfully
            return {"message": "User signed up successfully."}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())

@app.post("/login")
async def login(username: str, password: str):
    token_url = f"https://TestLaigo12.b2clogin.com/TestLaigo12.onmicrosoft.com/B2C_1_signInSignUp/oauth2/v2.0/token"
    RESOURCE_SCOPE = f"https://TestLaigo12.onmicrosoft.com/8ca3fe2b-8ae6-44a5-85a9-5652393faa0c/.default"
    payload = {
    'grant_type': 'password',
    'client_id': os.getenv("CLIENT_ID"),
    'scope': f'openid',
    'username': username,
    'password': password
}

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload,headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@app.post("/change-password")
async def change_password(data: ChangePassword):
    return AuthService.change_password(data)

@app.patch("/edit-profile")
async def edit_profile(data: EditProfile):
    return AuthService.edit_profile(data)

@app.get("/auth/get/token")
async def get_token(code: str):
    print(code)
    return {"access_token": code, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
