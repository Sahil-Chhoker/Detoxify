from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=8)


class ShowUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str

    class Config:  # tells pydantic to convert even non dict obj to json
        orm_mode = True
