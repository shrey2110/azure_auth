from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    username: EmailStr
    password: str
    display_name :str
    first_name :str
    last_name :str

class UserLogin(BaseModel):
    username: EmailStr
    password: str

class ChangePassword(BaseModel):
    username: EmailStr
    new_password: str

class EditProfile(BaseModel):
    username: EmailStr
    display_name: str
