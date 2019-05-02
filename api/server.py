import asyncio
import logging.config

import aiotask_context as context
from aiohttp import web

from api.config import config
from api.middlewares import correlation_id_middleware, error_middleware, json_middleware
from api.routes import routes
from api.signals import create_sentry, create_mongo


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)


def setup_middlewares(app):
    middlewares = [
        correlation_id_middleware,
        error_middleware,
        json_middleware,
    ]
    for middleware in middlewares:
        app.middlewares.append(middleware)


def on_startup_signal(app):
    # TODO add startup database
    app.on_startup.append(create_sentry)
    app.on_startup.append(create_mongo)


def on_cleanup_signal(app):
    # TODO add cleanup database
    pass


def init_app():
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)
    logging.config.dictConfig(config['LOGGING'])
    app = web.Application()
    setup_routes(app)
    setup_middlewares(app)
    on_startup_signal(app)
    on_cleanup_signal(app)
    return app


app = init_app()
