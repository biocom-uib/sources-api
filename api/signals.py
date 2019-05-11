import aiomysql
import aiopg

from api.config import config


async def create_psql_pool(app):
    app['psql_pool'] = {database: await create_pool_psql(database) for database in config['DATABASES']['psql']}


async def create_pool_psql(database):
    return await aiopg.create_pool(dbname=config[database]['db'], user=config[database]['user'], password=config[database]['pass'],
                                   host=config[database]['host'], port=config[database]['port'], minsize=1,
                                   maxsize=config[database]['max_pool_conn'])

async def dispose_psql_pool(app):
    for connection in app['psql_pool'].values():
        connection.close()
        await connection.wait_closed()


async def create_mysql_pool(app):
    app['mysql_pool'] = {database: await create_pool_mysql(database) for database in config['DATABASES']['mysql']}


async def create_pool_mysql(database):
    return await aiomysql.create_pool(
        host=config[database]['host'], port=config[database]['port'], user=config[database]['user'],
        password=config[database]['pass'], db=config[database]['db'], charset='utf8',
        minsize=1,  maxsize=config[database]['max_pool_conn'])

async def dispose_mysql_pool(app):
    for connection in app['mysql_pool'].values():
        connection.close()
        await connection.wait_closed()
