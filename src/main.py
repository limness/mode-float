from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import application_settings
from src.routers.uav_router import router as uav_router


def _include_routers(app: FastAPI):
    app.include_router(uav_router, prefix='/api/v1/uav')


def _configure_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.APP_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
        allow_headers=[
            'Content-Type',
            'Set-Cookie',
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Authorization',
        ],
    )
    # app.add_middleware(
    #     JWTMiddleware,
    #     exclude_paths=['/docs', '/openapi.json', '/health']
    # )


def create_app() -> FastAPI:
    app = FastAPI(
        title=application_settings.APP_TITLE,
        debug=application_settings.APP_DEBUG,
        version=application_settings.APP_VERSION,
        description='Tools for working with the Float Mode ID via the HTTP REST protocol',
        swagger_ui_parameters={'displayRequestDuration': True},
    )
    _configure_middlewares(app)
    _include_routers(app)
    return app
