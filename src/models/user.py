from typing import Annotated, Union
from pydantic import AfterValidator, EmailStr, StringConstraints, field_validator
from sqlmodel import Field, SQLModel
import re

from src.constants import ModelConstant
from src.types import WhiteSpaceStrippedStr

PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

def validate_password(value:str) -> str:
    """resuable passworfd validator"""
    if not PASSWORD_REGEX.match(value):
        raise ValueError("Password must be at least 8 characters long, include at least one uppercase letter, one number, and one special character.")
    return value

# We define a reusable Annoted passord type
MyPasswordStr = Annotated[
    WhiteSpaceStrippedStr,
    AfterValidator(validate_password)
]

PHONE_REGEX = re.compile(r"^\+243[(81)(82)(83)(80)(84)(85)(89)(97)(98)(99)(90)(91)]\d{13}$")

def validate_phone(value:str) -> str:
    """resuable phone validator"""
    if not PHONE_REGEX.match(value):
        raise ValueError("DRC Phone must have only 13 characters, start with +243, then contain one of these combinations : 81, 82, 83, 80, 84, 85, 89, 97, 98, 99, 90, 91 and ends with 7 decimal digits.")
    return value

# We define a reusable Annoted passord type
MyPhoneStr = Annotated[
    WhiteSpaceStrippedStr,
    AfterValidator(validate_password)
]

#class MyEmailStr(WhiteSpaceStrippedStr, EmailStr):
#    pass

"""
UserBaseModel: Model with main fields
"""
class UserBaseModel(SQLModel):
    name:WhiteSpaceStrippedStr = Field(max_length = ModelConstant.LEVEL_2_FIELD_MAX_LENGTH.value)
    email:EmailStr = Field(max_length = ModelConstant.LEVEL_2_FIELD_MAX_LENGTH.value)
    phone:MyPhoneStr | None = Field(default = None, max_length = 20)
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, value:str)-> str :
        return value.title()

"""
UserBDModel: Model that interacts with the Database
"""
class UserDBModel(UserBaseModel, table = True):
    __tablename__ = "users"
    id:int = ModelConstant.ID_FIELD.value
    password : str = Field(nullable = False)

class UserCreateModel(UserBaseModel):
    password:MyPasswordStr

# User Pulic
class UserPublicModel(SQLModel):
    id:int
    name:str
    phone:str
    email:str

# Partial User for Update
class UserUpdateModel(UserBaseModel):
    name:str | None
    email:EmailStr | None
    password:MyPasswordStr | None