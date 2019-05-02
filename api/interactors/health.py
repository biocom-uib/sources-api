from api.gateways.db import ping_postgres, ping_mysql


async def _db_health_mysql(db_connection):
    can_connect = await ping_mysql(db_connection)
    return can_connect


async def _db_health_postgres(db_connection):
    can_connect = await ping_postgres(db_connection)
    return can_connect


async def health(mysql_connection, postgres_connection):
    return {
        "mysql_connection": await _db_health_mysql(mysql_connection),
        "postgres_connection": await _db_health_postgres(postgres_connection),
    }
