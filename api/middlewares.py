import asyncio
import logging
import uuid
from json import dumps as json_dumps
from json.decoder import JSONDecodeError

import aiotask_context as context
from aiohttp import web

from api.config import config
from api.exceptions import ClientException
from api.utils import timing


logger = logging.getLogger(__name__)


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as e:
        return web.json_response(body=str(e), status=e.status_code)
    except ClientException as e:
        body = {'code': e.code, 'message': e.message, 'text': e.text}
        return web.json_response(body=json_dumps(body), status=e.status_code)
    except asyncio.CancelledError:  # pragma: nocover
        # do not mute asyncio.CancelledError
        raise
    except Exception as e:  # pylint: disable=broad-except
        if config['DEBUG']:
            raise
        return web.json_response(body=str(e), status=500)


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
    response.headers["X-Correlation-Id"] = context.get("X-Correlation-Id")
    return response
