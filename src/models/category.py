from sqlmodel import Field, SQLModel
from src.constants import ModelConstant

class CategoryBaseModel(SQLModel):
    name:str = Field(max_length = 100, unique = True)

class CategoryDBModel(CategoryBaseModel, table = True):
    __tablename__ = "categories"
    id:int = ModelConstant.ID_FIELD.value

class CategoryCreateModel(CategoryBaseModel):
    pass

class CategoryUpdateModel(CategoryBaseModel):
    pass

class CategoryPublicModel(CategoryBaseModel):
    id:str
