import asyncio
import logging.config

import aiotask_context as context
from aiohttp import web

from api.config import config
from api.middlewares import correlation_id_middleware, json_middleware, database_middleware, error_middleware
from api.routes import routes
from api.signals import create_psql_pool, create_mysql_pool, dispose_psql_pool, dispose_mysql_pool


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)


def setup_middlewares(app):
    middlewares = [
        correlation_id_middleware,
        error_middleware,
        json_middleware,
        database_middleware
    ]
    for middleware in middlewares:
        app.middlewares.append(middleware)


def on_startup_signal(app):
    app.on_startup.append(create_psql_pool)
    app.on_startup.append(create_mysql_pool)


def on_cleanup_signal(app):
    app.on_cleanup.append(dispose_psql_pool)
    app.on_cleanup.append(dispose_mysql_pool)



def init_app():
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)
    logging.config.dictConfig(config['LOGGING'])
    app = web.Application(handler_args={'keepalive_timeout': None})
    setup_routes(app)
    setup_middlewares(app)
    on_startup_signal(app)
    on_cleanup_signal(app)
    return app


app = init_app()
