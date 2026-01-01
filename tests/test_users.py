import uuid

from fastapi.testclient import TestClient

from app.api.injector_configuration import get_user_repository
from app.api.users.schemas import UserCreate, UserUpdate
from app.db.repository import UserRepository
from app.main import create_app
from app.models.user import UserInDB


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[str, UserInDB] = {}

    async def create(self, payload: UserCreate) -> UserInDB:
        new_id = uuid.uuid4().hex
        user = UserInDB(id=new_id, name=payload.name, email=payload.email)
        self._users[new_id] = user
        return user

    async def get_by_email(self, email: str) -> UserInDB | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def get_by_id(self, user_id: str) -> UserInDB | None:
        return self._users.get(user_id)

    async def list_users(self):
        return list(self._users.values())

    async def delete(self, user_id: str) -> bool:
        return self._users.pop(user_id, None) is not None

    async def update(self, user_id: str, payload: UserUpdate) -> UserInDB | None:
        if user_id not in self._users:
            return None
        existing = self._users[user_id]
        data = payload.model_dump(exclude_unset=True)
        updated = UserInDB(
            id=existing.id,
            name=data.get("name", existing.name),
            email=data.get("email", existing.email),
        )
        self._users[user_id] = updated
        return updated


def get_test_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


def get_test_client() -> TestClient:
    app = create_app(with_lifespan=False)
    repo = InMemoryUserRepository()

    async def _repo_dep() -> InMemoryUserRepository:
        return repo

    app.dependency_overrides[get_user_repository] = _repo_dep
    return TestClient(app)


def test_create_user_success():
    client = get_test_client()
    response = client.post("/users", json={"name": "Ada", "email": "ada@example.com"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ada"
    assert body["email"] == "ada@example.com"
    assert "id" in body


def test_unique_email_enforced():
    client = get_test_client()
    client.post("/users", json={"name": "Ada", "email": "ada@example.com"})
    response = client.post("/users", json={"name": "Grace", "email": "ada@example.com"})
    assert response.status_code == 400
    assert response.json()["detail"] == "email already exists"


def test_get_missing_user_returns_404():
    client = get_test_client()
    response = client.get("/users/nonexistent")
    assert response.status_code == 404


def test_delete_user():
    client = get_test_client()
    created = client.post("/users", json={"name": "Ada", "email": "ada@example.com"}).json()
    response = client.delete(f"/users/{created['id']}")
    assert response.status_code == 204


def test_update_user():
    client = get_test_client()
    created = client.post("/users", json={"name": "Ada", "email": "ada@example.com"}).json()
    response = client.put(
        f"/users/{created['id']}",
        json={"name": "Ada Lovelace", "email": "ada.lovelace@example.com"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ada Lovelace"
    assert body["email"] == "ada.lovelace@example.com"
