from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bson import ObjectId


def _stringify_object_id(obj_id: ObjectId | None) -> str:
    return str(obj_id) if obj_id is not None else ""


@dataclass(slots=True)
class UserInDB:
    id: str
    name: str
    email: str

    @classmethod
    def from_mongo(cls, document: dict[str, Any] | None) -> "UserInDB":
        if document is None:
            raise ValueError("Cannot build UserInDB from None")
        return cls(
            id=_stringify_object_id(document.get("_id")),
            name=document["name"],
            email=document["email"],
        )

    def to_public_dict(self) -> dict[str, str]:
        return {"id": self.id, "name": self.name, "email": self.email}
