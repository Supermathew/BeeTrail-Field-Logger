from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    email: EmailStr
    password_hash: str
    role: str = Field("beekeeper", description="Role of the user (beekeeper or admin)")


