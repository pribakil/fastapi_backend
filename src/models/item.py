from sqlmodel import Field, SQLModel
from src.constants import ModelConstant
from src.types import WhiteSpaceStrippedStr

class ItemBaseModel(SQLModel):
    name:WhiteSpaceStrippedStr = Field(max_length = ModelConstant.LEVEL_2_FIELD_MAX_LENGTH.value, unique = True)
    description:WhiteSpaceStrippedStr = Field(max_length = ModelConstant.LEVEL_1_FIELD_MAX_LENGTH.value)
    price:float | None = Field(default = 0.0, decimal_places=2, max_digits = 10)
    category_id:int = Field(gt = 0)

class ItemDBModel(ItemBaseModel, table = True):
    __tablename__ = "items"
    id:int = ModelConstant.ID_FIELD.value
    category_id:int = Field(foreign_key = "categories.id")

class ItemCreateModel(ItemBaseModel):
    pass

class ItemUpdateModel(ItemBaseModel):
    name:WhiteSpaceStrippedStr | None = Field(default = None, max_length = ModelConstant.LEVEL_2_FIELD_MAX_LENGTH.value, unique = True)
    description:WhiteSpaceStrippedStr | None = Field(default = None, max_length = ModelConstant.LEVEL_1_FIELD_MAX_LENGTH.value)

class ItemPublicModel(ItemBaseModel):
    id:int
    name:str
    description:str
    price:float
    category_id:int