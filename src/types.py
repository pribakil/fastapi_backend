from typing import Annotated

from pydantic import AfterValidator, StringConstraints

def remove_extra_space_in_str(value:str) -> str:
    return " ".join(value.split())

WhiteSpaceStrippedStr = Annotated[
    str,
    StringConstraints(strip_whitespace = True), # We remove white spaces around
    AfterValidator(remove_extra_space_in_str)   # We remove white extra spaces between
]