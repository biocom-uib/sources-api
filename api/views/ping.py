import logging

from aiohttp import web


logger = logging.getLogger(__name__)


async def pong(request):  # pylint: disable=unused-argument
    return web.json_response('pong')
