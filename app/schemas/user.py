from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    role: str = Field("beekeeper", description="Role of the user (beekeeper or admin)")

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    pass


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
