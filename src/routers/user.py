from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.services import user as userService
from src.models import UserDBModel, UserCreateModel, UserUpdateModel, UserPublicModel

from src.core.database import get_session

router_v1 = APIRouter(prefix = "/api/v1/users", tags = ["Users Endpoints : "])

@router_v1.post("/", response_model = UserPublicModel, deprecated=True, tags=["Deprecated since 2022"], description="This endpoint is deprecated, use /api/v2/users/ instead")
async def create_user(user:UserCreateModel, db:AsyncSession = Depends(get_session)):
    return await userService.create_user(db, user)

@router_v1.get("/", response_model = list[UserPublicModel], deprecated=True, tags=["Deprecated since 2022"], description="This endpoint is deprecated, use /api/v2/users/ instead")
async def read_user1(db:AsyncSession = Depends(get_session)):
    return await userService.read_users(db)

"""
Version 2 of the User API
"""
router_v2 = APIRouter(prefix = "/api/v2/users", tags = ["Users"])

@router_v2.post("/", response_model = UserPublicModel)
async def create_user(user:UserCreateModel, db:AsyncSession = Depends(get_session)) -> UserDBModel:
    return await userService.create_user_v2(db, user)

@router_v2.get("/", response_model = list[UserPublicModel])
async def read_user1(db:AsyncSession = Depends(get_session)):
    return await userService.read_users_v2(db)