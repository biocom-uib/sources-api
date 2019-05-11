from api.views.ping import pong
import api.views.stringdb as stringdb

routes_ping = [
   ['GET', '/ping', pong],

]
stringdb_routes = [
   ['GET', '/db/stringdb/items/proteins', stringdb.get_proteins],
   ['POST', '/db/stringdb/network/edges/select', stringdb.get_network_edges],
   ['POST', '/db/stringdb/bitscore/select', stringdb.get_bitscore],
   ['POST', '/db/stringdb/go/select', stringdb.get_go],

]

routes = routes_ping + stringdb_routes