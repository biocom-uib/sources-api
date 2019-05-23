import asyncio
import logging
import uuid
from json import dumps as json_dumps
from json.decoder import JSONDecodeError
from traceback import format_exc

import aiotask_context as context
from aiohttp import web

from api.config import config
from api.exceptions import ApiException, ErrorCodes
from api.utils import timing


logger = logging.getLogger(__name__)


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)

    except ApiException as e:
        data = {'ok': False, 'code': e.code, 'message': e.message, 'description': e.description}
        return web.json_response(data=data, status=e.status)

    except web.HTTPException as e:
        data = {'ok': False, 'code': ErrorCodes.UNKNOWN, 'message': f"Unknown HTTP exception was raised: {e}", 'description': e.text}
        return web.json_response(data=data, status=e.status)

    except asyncio.CancelledError:  # pragma: nocover
        # do not mute asyncio.CancelledError
        raise

    except Exception as e:  # pylint: disable=broad-except
        logger.exception('Unknown exception was raised')
        data = {'ok': False, 'code': ErrorCodes.UNKNOWN, 'message': f"Unknown exception was raised: {e}", 'description': None}
        return web.json_response(data=data, status=500)


@web.middleware
async def json_middleware(request, handler):
    try:
        request.post_json = {}
        if request.can_read_body:
            request.post_json = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='"Malformed Json Payload"')
    return await handler(request)


@web.middleware
async def correlation_id_middleware(request, handler):
    correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    context.set("X-Correlation-Id", correlation_id)
    response = await handler(request)
    # response.headers["X-Correlation-Id"] = context.get("X-Correlation-Id")
    return response


@web.middleware
async def database_middleware(request, handler):
    path = request.path.split('/')
    if path[1] != 'db':
        return await handler(request)
    database = path[2]
    if database in config['DATABASES']['mysql']:
        master_pool = request.app['mysql_pool'][database]
        async with master_pool.acquire() as master_connection:
            request.db = master_connection
            return await handler(request)
    if database in config['DATABASES']['psql']:
        master_pool = request.app['psql_pool'][database]
        async with master_pool.acquire() as master_connection:
            request.db = master_connection
            return await handler(request)
    return await handler(request)
