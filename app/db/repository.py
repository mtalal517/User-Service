from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.api.users.schemas import UserCreate, UserUpdate
from app.models.user import UserInDB


class UserRepository(ABC):
    """Abstract repository to allow DB-free testing."""

    @abstractmethod
    async def create(self, payload: UserCreate) -> UserInDB:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserInDB | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserInDB | None:
        raise NotImplementedError

    @abstractmethod
    async def list_users(self) -> Iterable[UserInDB]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user_id: str, payload: UserUpdate) -> UserInDB | None:
        raise NotImplementedError


class MongoUserRepository(UserRepository):
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def create(self, payload: UserCreate) -> UserInDB:
        result = await self._collection.insert_one(payload.model_dump())
        doc = await self._collection.find_one({"_id": result.inserted_id})
        return UserInDB.from_mongo(doc)

    async def get_by_email(self, email: str) -> UserInDB | None:
        doc = await self._collection.find_one({"email": email})
        return UserInDB.from_mongo(doc) if doc else None

    async def get_by_id(self, user_id: str) -> UserInDB | None:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self._collection.find_one({"_id": ObjectId(user_id)})
        return UserInDB.from_mongo(doc) if doc else None

    async def list_users(self) -> Iterable[UserInDB]:
        cursor = self._collection.find({})
        return [UserInDB.from_mongo(doc) async for doc in cursor]

    async def delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = await self._collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count == 1

    async def update(self, user_id: str, payload: UserUpdate) -> UserInDB | None:
        if not ObjectId.is_valid(user_id):
            return None
        update_doc = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if not update_doc:
            doc = await self._collection.find_one({"_id": ObjectId(user_id)})
            return UserInDB.from_mongo(doc) if doc else None
        await self._collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_doc})
        doc = await self._collection.find_one({"_id": ObjectId(user_id)})
        return UserInDB.from_mongo(doc) if doc else None
