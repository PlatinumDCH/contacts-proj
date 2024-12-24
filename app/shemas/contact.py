from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from  datetime import date

"""
CreareContact(first_name, last_name, email, phone_number,)
    - добваить поле date_birthday:date
"""


class CreateContact(BaseModel):
    first_name:str = Field(min_length=1, max_length=50)
    last_name:str = Field(min_length=1, max_length=50)
    email: EmailStr
    note: Optional[str]
    phone_number:str
    date_birthday:date
    
class ContactResponse(CreateContact):
    id:int
    model_config = ConfigDict(from_attribute=True)
