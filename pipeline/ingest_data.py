#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

# tipos corretos de cada coluna
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

# colunas que são datas
parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=9876, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option('--year', default=2021, type=int, help='Dataset year')
@click.option('--month', default=1, type=int, help='Dataset month')
def run(pg_user, pg_password, pg_host, pg_port, pg_db, target_table, year, month):

    chunksize = 100000

    # constroi a url do arquivo .csv
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}yellow_tripdata_{year}-{month:02d}.csv.gz'

    # cria a conexão com o banco de dados
    engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    # lê o csv em chunks (obs: o df_iter não precisa estar dentro do for para funcionar)
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True, # irá iterar sobre cada chunk (a depender do chunksize)
        chunksize=chunksize
    )

    first = True
    for df_chunk in tqdm(df_iter):
        if first:
            # cria uma tabela vazia com os tipos corretos, caso já exista a tabela com o mesmo nome
            # dropa e cria outra do zero
            df_chunk.head(0).to_sql(
                name=target_table, 
                con=engine, 
                if_exists='replace'
                )
            first = False

        # adiciona o chunk atual na tabela
        df_chunk.to_sql(
            name=target_table, 
            con=engine, 
            if_exists='append'
            )
        
    df_zones = pd.read_csv('https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')
    df_zones.to_sql(
        name='zones',
        con=engine,
        if_exists='replace',
        index=False
        )
        
    pass
        
if __name__ == '__main__':
    run()