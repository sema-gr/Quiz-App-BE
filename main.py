from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health


def create_app():
    app = FastAPI(title="FastAPI Project", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
    )

    app.include_router(health.router)

    return app


app = create_app()
