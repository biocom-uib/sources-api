import asyncio
import csv
import aiopg
from api.config import config

database = 'isobase'
SPECIES_LIST = ['cel']
files = {'cel': 'files/isobase/ce.tab'}

mapping = {'cel': {'name': 'Caenorhabditis elegans', 'id': 6239}}


def get_edges(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(csv_file)
        return list(reader)


async def create_table(db_connection):
    create_mapping_statment = """
        CREATE TABLE species (
            id          integer,
            name        text
        );
    """

    create_table_statment = """
        CREATE TABLE networks (
            species_id     integer REFERENCES species (id) ON DELETE CASCADE,
            protein_1      text,
            protein_2      text,
            PRIMARY KEY (speecies_id, protein_1, protein_2)
        );
    """

    create_index_statment = "CREATE_INDEX idx_species_id ON networks(species_id);"
    await db_connection.execute(create_mapping_statment)
    await db_connection.execute(create_table_statment)
    await db_connection.execute(create_index_statment)



async def create_species_mapping(db_connection):
    values = ','.join(f"({species['id']}, {species['name']})" for species in mapping.values())
    insert_statment = f"INSERT INTO species (id, name) VALUES {values};"
    await db_connection.execute(insert_statment)
    

def write_edges(db_connection, species_id, rows):
    values = ','.join(f"({species_id}, {row['INTERACTOR_A']}, {row['INTERACTOR_B']})" for row in rows)
    insert_statment = f"INSERT INTO networks (species_id, protein_1, protein_2) VALUES {values};"
    await db_connection.execute(insert_statment)

async def main():
    db_connection =  await aiopg.create_pool(dbname=config[database]['db'], user=config[database]['user'], password=config[database]['pass'],
                                    host=config[database]['host'], port=config[database]['port'], minsize=1,
                                    maxsize=config[database]['max_pool_conn'])

    await create_table(db_connection)
    await create_species_mapping(db_connection)
    [write_edges(db_connection, mapping[species]['id'], get_edges(files[species])) for species in SPECIES_LIST]

if __name__ == 'main':
    asyncio.run(main())