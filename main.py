from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.db.redis import redis_client
from app.routers import (
    company_membership_router,
    health,
    user_router,
    auth_router,
    company_router,
)


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Project", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(user_router.router)
    app.include_router(auth_router.router)
    app.include_router(company_router.router)
    app.include_router(company_membership_router.router)

    @app.on_event("startup")
    async def startup_event():
        await redis_client.connect()

    @app.on_event("shutdown")
    async def shutdown_event():
        await redis_client.disconnect()

    return app


app = create_app()
