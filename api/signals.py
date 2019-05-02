from api.config import config


# async def create_mysql_pool(app):
#     app['mysql_pool'] = await aiomysql.create_pool(
#         host=config['MYSQL_HOST'], port=config['MYSQL_PORT'], user=config['MYSQL_USER'],
#         password=config['MYSQL_PASS'], db=config['MYSQL_DB'], charset='utf8', minsize=config['MYSQL_MIN_POOL_CONN'],
#         maxsize=config['MYSQL_MAX_POOL_CONN'], autocommit=False, pool_recycle=config['MYSQL_POOL_RECYCLE'])


# async def dispose_mysql_pool(app):
#     app['mysql_pool'].close()
#     await app['mysql_pool'].wait_closed()
