import logging

from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.core.settings import application_settings

logger = logging.getLogger(__name__)


async def metrics_handler(request):
    try:
        resp = web.Response(body=generate_latest(), headers={'Content-Type': CONTENT_TYPE_LATEST})
        return resp
    except Exception as e:
        logger.error(f'Error generating prometheus metrics: {e!s}')
        return web.Response(status=500, text='Internal Server Error')


def create_app():
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    logger.info('Aiohttp prometheus app created and /metrics route registered')
    return app


async def start_prometheus():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner, application_settings.APP_PROMETHEUS_HOST, application_settings.APP_PROMETHEUS_PORT
    )
    await site.start()
    logger.info(
        f'Prometheus server started on {application_settings.APP_PROMETHEUS_HOST}:{application_settings.APP_PROMETHEUS_PORT}'
    )
