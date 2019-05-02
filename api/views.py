import logging

from aiohttp import web
from api.interactors.health import health as health_interactor


logger = logging.getLogger(__name__)


async def pong(request):  # pylint: disable=unused-argument
    return web.json_response('pong')


async def health_check(request):
    response = await health_interactor(request.app['mysql_db'], request.app['postgres_db'])
    status = 200 if all(v for v in response.values()) else 500
    return web.json_response(response, status=status)
