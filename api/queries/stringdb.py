import aiopg
import numpy as np
import pandas as pd

import psycopg2.sql as sql


class StringDB(object):
    SPECIES_COLUMNS = {
        'species_id': int,
        'official_name': str,
        'compact_name': str,
        'kingdom': str,
        'type': str,
        'protein_count': int
    }

    PROTEINS_COLUMNS = {
        'protein_id': int,
        'protein_external_id': str,
        'species_id': int,
        'protein_checksum': str,
        'protein_size': int,
        'annotation': str,
        'preferred_name': str
        # 'annotation_word_vectors':
    }

    EVIDENCE_SCORE_TYPES = {
        'equiv_nscore':                    1,
        'equiv_nscore_transferred':        2,
        'equiv_fscore':                    3,
        'equiv_pscore':                    4,
        'equiv_hscore':                    5,
        'array_score':                     6,
        'array_score_transferred':         7,
        'experimental_score':              8,
        'experimental_score_transferred':  9,
        'database_score':                  10,
        'database_score_transferred':      11,
        'textmining_score':                12,
        'textmining_score_transferred':    13,
        'neighborhood_score':              14,
        'fusion_score':                    15,
        'cooccurence_score':               16
    }


    @staticmethod
    async def init_pool(*, host='stringdb', port=5432, user='stringdb', password='stringdb', dbname='stringdb'):
        return await aiopg.create_pool(host=host, port=port, user=user, password=password, dbname=dbname, timeout=None)


    def __init__(self, *, host='stringdb', port=5432, user='stringdb', password='stringdb', dbname='stringdb', pool=None):
        self.pool = pool
        self.conn = None

        if pool is None:
            self.host = host
            self.port = port
            self.user = user
            self.password = password
            self.dbname = dbname


    async def connect(self):
        if self.pool is None:
            self.conn = await aiopg.connect(host=self.host, port=self.port, user=self.user, password=self.password, dbname=self.dbname, timeout=None)


    async def disconnect(self):
        if self.conn is not None and not self.conn.closed:
            await self.conn.close()
            self.conn = None


    async def __aenter__(self):
        await self.connect()
        return self


    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()


    def cursor(self):
        if self.pool is not None:
            return self.pool.cursor()
        else:
            return self.conn.cursor()

    async def _select_with_filters(self, table_sql, columns, filters):
        query_filters = []
        placeholders = {}

        if len(filters) >= 0:
            for filter_col, filter_vals in filters.items():
                query_filters.append(sql.SQL('{0} in {1}').format(sql.Identifier(filter_col), sql.Placeholder(name=filter_col)))
                placeholders[filter_col] = tuple(filter_vals)
        else:
            query_filters.append(sql.SQL('true'))

        query = sql.SQL('select {columns} from {table} where {where}').format(
            columns = sql.SQL(', ').join(map(sql.Identifier, columns)),
            table = table_sql,
            where = sql.SQL(' and ').join(query_filters))

        async with self.cursor() as cursor:
            await cursor.execute(query, placeholders)
            rows = await cursor.fetchall()

        return pd.DataFrame(rows, columns=columns)


    async def get_species(self, columns, filters):
        return await self._select_with_filters(sql.SQL('items.species'), columns, filters)


    async def get_proteins(self, columns, filters):
        return await self._select_with_filters(sql.SQL('items.proteins'), columns, filters)


    # async def get_protein_sequences(self, filters):
    #     proteins = Table('proteins', schema='items')
    #     sequences = Table('proteins_sequences', schema='items')

    #     query = Query.from_(sequences)

    #     if not set(filters.keys()).issubset({'protein_id', 'sequence'}):
    #         query = query.join(proteins).on_field('protein_id')

    #     sql = query \
    #         .select(sequences.protein_id, sequences.sequence) \
    #         .where(self._make_criterion(filters, {'protein_id': proteins.protein_id})) \
    #         .get_sql()

    #     async with self.cursor() as cursor:
    #         await cursor.execute(sql)
    #         rows = await cursor.fetchall()

    #     return pd.DataFrame(rows, columns=['protein_id', 'sequence'])


    async def get_weighted_network(self, species_id, score_type, threshold):
        placeholders = {'species_id': species_id, 'threshold': threshold}

        if score_type == 'combined_score':
            query = sql.SQL("""
                select
                  node_id_a,
                  node_id_b,
                  combined_score
                from
                  network.node_node_links
                where
                  species_id = {species_id}
                  and
                  combined_score >= {threshold}
                """).format(
                    species_id = Placeholder(name='species_id'),
                    threshold = Placeholder(name='threshold'))

        else:
            score_type_id = StringDB.EVIDENCE_SCORE_TYPES[score_type]
            placeholders['score_type_id'] = score_type_id

            query = sql.SQL("""
                with indexed as (
                  select
                    node_id_a,
                    node_id_b,
                    unnest(evidence_scores[:][1:1]) score_type,
                    unnest(evidence_scores[:][2:2]) score
                  from
                    network.node_node_links
                  where
                    node_type_b = {species_id}
                )
                select
                  node_id_a,
                  node_id_b,
                  score as {score_type}
                from
                  indexed
                where
                  score_type = {score_type_id}
                  and
                  score >= {threshold}
                """).format(
                    species_id = sql.Placeholder(name='species_id'),
                    threshold = sql.Placeholder(name='threshold'),
                    score_type = sql.Identifier(score_type),
                    score_type_id = sql.Placeholder(name='score_type_id'))


        async with self.cursor() as cursor:
            await cursor.execute(query, placeholders)
            edges = await cursor.fetchall()

        return pd.DataFrame(edges, columns=['node_id_a', 'node_id_b', score_type])



    async def get_network(self, species_id, score_thresholds):
        placeholders = {'species_id' : species_id}

        if not score_thresholds:
            query = sql.SQL('select node_id_a, node_id_b from items.node_node_links where node_type_b = {species_id}').format(
                species_id = sql.Placeholder(name='species_id'))

        else:
            wheres = []

            for score_type, threshold in score_thresholds.items():
                score_type_id = StringDB.EVIDENCE_SCORE_TYPES[score_type]
                placeholders[score_type] = threshold

                wheres.append(
                    sql.SQL('(score_type = {0} and score >= {1})').format(
                        sql.Literal(score_type_id),
                        sql.Placeholder(name=score_type)))

            query = sql.SQL("""
                with indexed as (
                  select
                    node_id_a,
                    node_id_b,
                    unnest(evidence_scores[:][1:1]) score_type,
                    unnest(evidence_scores[:][2:2]) score
                  from
                    network.node_node_links
                  where
                    node_type_b = {0}
                )
                select distinct
                  node_id_a,
                  node_id_b
                from
                  indexed
                where
                  {1}
                """).format(
                    sql.Placeholder(name='species_id'),
                    sql.SQL(' or ').join(wheres))

        async with self.cursor() as cursor:
            await cursor.execute(query, placeholders)
            edges = await cursor.fetchall()

        return pd.DataFrame(edges, columns=['node_id_a', 'node_id_b'])


    async def get_bitscore_matrix(self, net1_species_ids, net1_protein_ids, net2_species_ids, net2_protein_ids):
        async with self.cursor() as cursor:
            await cursor.execute("""
                with
                    net1_prot_ids as (select unnest(%(net1_protein_ids)s :: integer[]) net1_prot_id),
                    net2_prot_ids as (select unnest(%(net2_protein_ids)s :: integer[]) net2_prot_id)
                select
                  protein_id_a, protein_id_b, bitscore
                from
                  homology.blast_data blast
                where
                  species_id_a in %(net1_species_ids)s
                  and
                  species_id_b in %(net2_species_ids)s
                  and
                  protein_id_a in (select net1_prot_id from net1_prot_ids)
                  and
                  protein_id_b in (select net2_prot_id from net2_prot_ids);
                """,
                {'net1_species_ids': tuple(net1_species_ids),
                 'net2_species_ids': tuple(net2_species_ids),
                 'net1_protein_ids': list(net1_protein_ids),
                 'net2_protein_ids': list(net2_protein_ids)})

            values = await cursor.fetchall()

        return pd.DataFrame(values, columns=['protein_id_a', 'protein_id_b', 'bitscore'])


    async def get_ontology_mapping(self, species_ids):
        async with self.cursor() as cursor:
            await cursor.execute("""
                select
                  p.protein_external_id,
                  array_agg(distinct g.go_id)
                from
                  mapping.gene_ontology g
                inner join
                  items.proteins p on p.protein_id = g.string_id
                where
                  g.species_id in %(species_ids)s
                  and
                  g.evidence_code in ('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'IC')
                group by
                  p.protein_external_id;
                """,
                {'species_ids': tuple(species_ids)})

            rows = await cursor.fetchall()

        return dict(rows)


    async def get_string_go_annotations(self, protein_ids=None, taxid=None):
        if protein_ids is not None:
            async with self.cursor() as cursor:
                await cursor.execute("""
                    select protein_id, go_id
                    from go.explicit_by_id
                    where protein_id = ANY(%(protein_ids)s);
                    """,
                    {'protein_ids': protein_ids})

                rows = await cursor.fetchall()

            return rows if rows else None

        if taxid is not None:
            async with self.cursor() as cursor:
                await cursor.execute("""
                    select gos.protein_id, gos.go_id
                    from (select *
                          from items.proteins
                          where species_id = %(species_id)s) as proteins
                    left join go.explicit_by_id as gos
                        on proteins.protein_id = gos.protein_id;
                    """,
                    {'species_id': taxid})

                rows = await cursor.fetchall()

            return rows if rows else None
