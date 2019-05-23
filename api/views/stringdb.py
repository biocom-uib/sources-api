import json
import msgpack

import logging

from aiohttp import web

from api.queries.stringdb import StringDB
from api.exceptions import ErrorCodes, raise_bad_request, ensure_key_as, ensure_list_of


logger = logging.getLogger(__name__)


def dataframe_response(request, df):
    for accept in request.headers.get('Accept', '*/*').split(','):
        accept = accept.strip()

        if accept.startswith('*/*') or accept.startswith('text/*') or accept.startswith('text/tab-separated-values'):
            body = df.to_csv(sep='\t', index=False)
            return web.Response(text=body, content_type='text/tab-separated-values')

        if accept.startswith('application/*') or accept.startswith('application/x-msgpack'):
            body = msgpack.packb({col: df[col].tolist() for col in df.columns})
            return web.Response(body=body, content_type='application/x-msgpack')

        if accept.startswith('application/json'):
            body = {col: df[col].tolist() for col in df.columns}
            return web.json_response(body)


def json_response(request, obj):
    for accept in request.headers.get('Accept', '*/*').split(','):
        accept = accept.strip()

        if accept.startswith('*/*') or accept.startswith('application/json'):
            return web.json_response(obj)

        if accept.startswith('application/x-msgpack'):
            body = msgpack.packb(obj)
            return web.Response(body=body, content_type='application/x-msgpack')


async def get_proteins(request):
    stringdb = StringDB(pool=request.db)
    columns = ensure_list_of(str, 'columns', request.post_json)

    filters = ensure_key_as(dict, 'filter', request.post_json)

    if len(filters) == 0:
        raise_bad_request(ErrorCodes.MISSING_PARAMETER, "no filters specified for protein search")

    for col in columns:
        if col not in StringDB.PROTEINS_COLUMNS:
            raise_bad_request(ErrorCodes.BAD_KEY, 'Unknown column: ' + col, "Available columns: " + ', '.join(StringDB.PROTEINS_COLUMNS))

    for filter_key in filters.keys():
        if filter_key not in StringDB.PROTEINS_COLUMNS:
            raise_bad_request(ErrorCodes.BAD_KEY, 'Unknown filter: ' + col, "Available filters: " + ', '.join(StringDB.PROTEINS_COLUMNS))

        ensure_list_of(StringDB.PROTEINS_COLUMNS[filter_key], filter_key, filters)

    df = await stringdb.get_proteins(columns, filters)

    return dataframe_response(request, df)


async def get_network_edges(request):
    stringdb = StringDB(pool=request.db)

    species_id = ensure_key_as(int, 'species_id', request.post_json)
    score_thresholds = ensure_key_as(dict, 'score_thresholds', request.post_json)

    for score_type, threshold in score_thresholds.items():
        if score_type not in StringDB.EVIDENCE_SCORE_TYPES:
            raise_bad_request(ErrorCodes.BAD_KEY, 'Unknown score type: ' + score_type)

        if not isinstance(threshold, int):
            raise_bad_request(ErrorCodes.BAD_KEY, 'score thresholds must be integers')

    df = await stringdb.get_network(species_id, score_thresholds)

    return dataframe_response(request, df)


async def get_bitscore(request):
    stringdb = StringDB(pool=request.db)

    net1_species_ids = ensure_list_of(int, 'net1_species_ids', request.post_json)
    net1_protein_ids = ensure_list_of(int, 'net1_protein_ids', request.post_json)
    net2_species_ids = ensure_list_of(int, 'net2_species_ids', request.post_json)
    net2_protein_ids = ensure_list_of(int, 'net2_protein_ids', request.post_json)

    df = await stringdb.get_bitscore_matrix(
            net1_species_ids=net1_species_ids, net1_protein_ids=net1_protein_ids,
            net2_species_ids=net2_species_ids, net2_protein_ids=net2_protein_ids)

    return dataframe_response(request, df)


async def get_go(request):
    stringdb = StringDB(pool=request.db)

    species_ids = ensure_list_of(int, 'species_ids', request.post_json)
    go_mapping = await stringdb.get_ontology_mapping(species_ids)

    return json_response(request, go_mapping)

