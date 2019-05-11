import msgpack

import logging

from aiohttp import web


logger = logging.getLogger(__name__)


async def get_proteins(request):
    columns = request.query.get('columns')
    species_id = request.query.get('species_id')
    external_id = request.query.get('external_id') 

    body = {'column1': ['p1', 'p2', 'p3']}

    return web.Response(body=msgpack.packb(body), content_type='application/x-msgpack')


async def get_network_edges(request):
    body = request.post_json
    return web.Response(body=msgpack.packb(body), content_type='application/x-msgpack')

async def get_bitscore(request):
    body = request.post_json
    return web.Response(body=msgpack.packb(body), content_type='application/x-msgpack')

async def get_go(request):
    body = request.post_json
    return web.Response(body=msgpack.packb(body), content_type='application/x-msgpack')