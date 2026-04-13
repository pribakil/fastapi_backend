from warnings import deprecated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import UserDBModel, UserCreateModel, UserUpdateModel

@deprecated("use the create_user_v2 instead.")
async def create_user(db:AsyncSession, user:UserCreateModel):
    new_user = UserDBModel(name = user.name, email = user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@deprecated("use the read_users_v2 instead.")
async def read_users(db:AsyncSession):
    result = await db.execute(select(UserDBModel))
    return result.scalars().all()

"""
Version 2 of User Service
"""
async def create_user_v2(db:AsyncSession, user:UserCreateModel) -> UserDBModel:
    new_user = UserDBModel(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def read_users_v2(db:AsyncSession) -> list[UserDBModel]:
    result = await db.execute(select(UserDBModel))
    return result.scalars().all()

async def read_user_by_id(db:AsyncSession, user_id:int) -> UserDBModel | None:
    result = await db.execute(select(UserDBModel).where(UserDBModel.id == user_id))
    return result.scalar_one_or_none()

async def update_user_v2(db:AsyncSession, user_id:int, user:UserUpdateModel) -> UserDBModel | None:
    user_db = await read_user_by_id(db, user_id)
    if not user_db:
        return None
    user_updated_data = user.model_dump(exclude_unset = True)
    user_db.sqlmodel_update(user_updated_data)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return user_db

async def delete(db:AsyncSession, user_id:int) -> bool:
    user_db = await read_user_by_id(db, user_id)
    if not user_db:
        return False
    
    db.delete(user_db)
    await db.commit()
    return True

async def filter(db:AsyncSession, name:str | None, email:str | None) -> list[UserDBModel] | None:
    query = select(UserDBModel)
    if name:
        query = query.where(UserDBModel.name == name)
    if email:
        query = query.where(UserDBModel.email == email)
    result = await db.execute(query)
    return result.scalars().all()