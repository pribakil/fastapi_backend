from fastapi import APIRouter
from src.libs.arbo20.main import get_arbo20_models

router = APIRouter(prefix = "/api/v1/arbo20_grids", tags = ["Arbotwenty Grids"])

@router.get("/")
def read_grids(page:int = 1, size:int = 100, center:int | None = None):
    return get_arbo20_models(page, size, center)