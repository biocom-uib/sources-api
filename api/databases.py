from contextlib import AbstractAsyncContextManager

from api.config import config
from api.exceptions import ErrorCodes, raise_http_error


class DBConnections(AbstractAsyncContextManager):
    def __init__(self, app):
        self.app = app
        self.connections = dict()


    async def get_connection(self, db_name):
        if db_name in self.connections:
            return self.connections[db_name]['handle']

        elif db_name in config['DATABASES']['mysql']:
            mgr = self.app['mysql_pool'][db_name].acquire()

        elif db_name in config['DATABASES']['psql']:
            mgr = self.app['psql_pool'][db_name].acquire()

        else:
            raise_http_error(
                ErrorCodes.RESOURCE_UNAVAILABLE,
                f'requested database is not configured: {db_name}')

        aexit = type(mgr).__aexit__

        connection = await mgr.__aenter__()

        self.connections[db_name] = {
            'aexit': lambda *args, **kwargs: aexit(mgr, *args, **kwargs),
            'handle': connection
        }

        return connection


    async def __aexit__(self, exc_type, exc_value, traceback):
        result = None

        for conn in self.connections.values():
            result = result or await conn['aexit'](exc_type, exc_value, traceback)

        return result
