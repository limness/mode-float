import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.settings import application_settings
from backend.middleware import JWTMiddleware
from backend.routers.uav_router import router as uav_router
from backend.routers.user_router import router as user_router


def _include_routers(app: FastAPI):
    app.include_router(uav_router, prefix='/api/v1/uav')
    app.include_router(user_router, prefix='/api/v1/users')


def _mount(app: FastAPI):
    class SPAStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope):
            full_path, stat_result = self.lookup_path(path)
            if stat_result:
                return await super().get_response(path, scope)

            index_file = os.path.join(self.directory, 'index.html')
            return FileResponse(index_file)

    app.mount(
        '/',
        SPAStaticFiles(directory=os.path.join(os.path.dirname(__file__), './static'), html=True),
        name='static',
    )


def _configure_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.APP_ALLOWED_ORIGINS,
        allow_credentials=False,
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
    app.add_middleware(JWTMiddleware, exclude_paths=['/docs', '/openapi.json', '/health'])


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
    _mount(app)
    return app
