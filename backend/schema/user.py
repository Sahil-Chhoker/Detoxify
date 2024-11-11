from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import UUID4


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    message: str
    created_at: str

    class Config:  # tells pydantic to convert even non dict obj to json
        from_attributes = True


class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: str