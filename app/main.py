from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import users
from app.core.config import get_settings
from app.db.mongodb import MongoConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.mongo_manager = MongoConnectionManager(settings)
    async for _ in app.state.mongo_manager.connect():
        yield


def create_app(with_lifespan: bool = True) -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan if with_lifespan else None,
    )
    application.include_router(users.router)

    @application.get("/", include_in_schema=False)
    async def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return application


app = create_app()
