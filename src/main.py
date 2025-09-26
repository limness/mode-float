import sys
import os
from contextlib import asynccontextmanager

# from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status, Request, FastAPI, Depends
from src.core.settings import application_settings
# from pygelf import GelfTcpHandler
# from loguru import logger

# from src.routers.user_router import app as user_router
# from src.routers.auth_router import app as auth_router
# from src.core.settings import application_settings
# from src.core.database import postgres_async_engine
# from src.models import oauth_model, user_model
# from src.exc import app_unexpected_handler


def _include_routers(app: FastAPI):
    # app.include_router(user_router, prefix="/api/v1/users")
    ...


def _configure_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.APP_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Authorization",
        ],
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title=application_settings.APP_TITLE,
        debug=application_settings.APP_DEBUG,
        version=application_settings.APP_VERSION,
        description="Tools for working with the Float Mode ID via the HTTP REST protocol",
        swagger_ui_parameters={"displayRequestDuration": True},
    )
    security = HTTPBearer()

    @app.get("/api/me")
    def me(creds: HTTPAuthorizationCredentials = Depends(security)):
        claims = verify(creds)
        return {"sub": claims["sub"], "roles": claims.get("realm_access", {}).get("roles", [])}

    _configure_middlewares(app)
    _include_routers(app)
    return app


def verify(creds: HTTPAuthorizationCredentials):
    try:
        print('creds.credentials', creds.credentials)
        return jwt.decode(
            creds.credentials,
            jwks(),
            algorithms=["RS256"],
            audience=AUD,
            issuer=ISSUER,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
