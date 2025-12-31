from fastapi import HTTPException, status

from app.db.repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def create_user(self, payload: UserCreate) -> UserResponse:
        existing = await self._repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")
        user = await self._repo.create(payload)
        return UserResponse.model_validate(user.to_public_dict())

    async def list_users(self) -> list[UserResponse]:
        users = await self._repo.list_users()
        return [UserResponse.model_validate(u.to_public_dict()) for u in users]

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
        return UserResponse.model_validate(user.to_public_dict())

    async def delete_user(self, user_id: str) -> None:
        deleted = await self._repo.delete(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    async def update_user(self, user_id: str, payload: UserUpdate) -> UserResponse:
        if payload.email is not None:
            existing = await self._repo.get_by_email(payload.email)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")
        user = await self._repo.update(user_id, payload)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
        return UserResponse.model_validate(user.to_public_dict())
