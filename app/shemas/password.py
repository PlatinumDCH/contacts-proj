from pydantic import BaseModel, EmailStr, Field

class ResetPasswordSchema(BaseModel):
    email:EmailStr

class ConfirmPassword(BaseModel):
    token:str
    new_password:str = Field(min_length=3, max_length=6)