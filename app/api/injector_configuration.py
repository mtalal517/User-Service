from fastapi import Depends, Request

from app.api.users.services import UserService
from app.db.mongodb import MongoConnectionManager
from app.db.repository import MongoUserRepository, UserRepository


def get_user_repository(request: Request) -> UserRepository:
    manager: MongoConnectionManager = request.app.state.mongo_manager
    return MongoUserRepository(manager.collection())


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)
