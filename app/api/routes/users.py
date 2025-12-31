from fastapi import APIRouter, Depends, status

from app.api.dependencies.db import get_user_service
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return await service.create_user(payload)


@router.get("", response_model=list[UserResponse])
async def list_users(service: UserService = Depends(get_user_service)) -> list[UserResponse]:
    return await service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)) -> UserResponse:
    return await service.get_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)) -> None:
    await service.delete_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, payload: UserUpdate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return await service.update_user(user_id, payload)
