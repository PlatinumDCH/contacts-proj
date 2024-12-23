from pydantic import BaseModel, Field, EmailStr

class UserSchema(BaseModel):
    username:str = Field(min_length=3, max_length=6)
    email: EmailStr
    password:str = Field(min_length=3, max_length=5)

class UserResponse(BaseModel):
    id:int
    username:str
    email:str

class NewUserSchema(UserSchema):
    avatart: str|None = None
