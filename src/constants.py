from enum import Enum

from sqlmodel import Field

class ModelConstant(Enum):
    LEVEL_1_FIELD_MAX_LENGTH = 510
    LEVEL_2_FIELD_MAX_LENGTH = 255
    LEVEL_3_FIELD_MAX_LENGTH = 125
    ID_FIELD = Field(primary_key = True, index = True)