from api.views import pong, health_check
routes = [
   ['GET', '/ping', pong],
   ['GET', '/health', health_check]
]