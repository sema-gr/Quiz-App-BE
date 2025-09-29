from fastapi import FastAPI
from app.routers import health


def create_app():
    app = FastAPI(title="FastAPI Project", version="0.1.0")

    app.include_router(health.router)

    return app


app = create_app()
