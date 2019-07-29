from api.views.ping import pong
import api.views.stringdb as stringdb

routes_ping = [
   ['GET', '/ping', pong],

]
stringdb_routes = [
   ['POST', '/db/stringdb/items/species/select',   stringdb.select_species],
   ['POST', '/db/stringdb/items/proteins/select',  stringdb.select_proteins],
   ['POST', '/db/stringdb/network/edges/select',   stringdb.select_network_edges],
   ['GET',  '/db/stringdb/network/edges/weighted', stringdb.get_weighted_network_edges],
   ['POST', '/db/stringdb/bitscore/select',        stringdb.select_bitscores],
   ['POST', '/db/stringdb/go/annotations/select',  stringdb.select_go_annotations],

]

routes = routes_ping + stringdb_routes
