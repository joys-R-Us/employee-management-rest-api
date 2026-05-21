from __future__ import annotations

from fastapi import FastAPI

from app.auth.loader import load_env
from app.auth.middleware import JWTAuthMiddleware
from app.auth.route import auth as auth_routes
from app.auth.route import employee as employee_routes

from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Ensure models are registered with SQLAlchemy metadata
from app import models  # noqa: F401


def create_app() -> FastAPI:

    load_env()

    # Create all database tables based on your SQLAlchemy models
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Employee Management API")


    # CORS: allow only trusted frontend origins.
    # In production, set `allow_origins` to your real domain(s) (not "*").
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Step 10: Protect all endpoints globally.
    # Skip auth endpoints so users can login/register.
    app.add_middleware(
        JWTAuthMiddleware,
        # Exclude endpoints users must access without a token.
        # Also exclude Swagger/Redoc assets used by /docs.
        excluded_paths=[
            "/auth/login",
            "/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
        ],
    )




    app.include_router(auth_routes.router)
    app.include_router(employee_routes.router)

    return app


app = create_app()


