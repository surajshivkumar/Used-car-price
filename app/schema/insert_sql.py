import configparser
import psycopg2
import psycopg2.extras
import sys
import time
import os
import pandas as pd 

def get_sql_conn(sql_conf: configparser.SectionProxy, dbname: str = None):
    if dbname is None:
        dbname = sql_conf.get('dbname')
    prodution_db = psycopg2. \
        connect(host=sql_conf['host'],
                database=sql_conf['dbname'],
                user=sql_conf['user'],
                password=sql_conf['password'])
    return prodution_db

def get_confg(path: str):
    config = configparser.ConfigParser()
    _ = config.read(path)
    return config

def push_to_sql(data: pd.DataFrame, config: configparser.ConfigParser):
    table = config['sql-table']['table_all_cars']
    pk = config['sql-table']['table_all_cars_pk']
    df_columns = list(data)
    columns = ",".join(df_columns)
    values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
    updates = ','.join([col + '=excluded.' + col for col in df_columns])
    insert_stmt = "INSERT INTO {} ({}) {} ON CONFLICT ({}) DO UPDATE SET {}". \
        format(table, columns, values, pk, updates)
    print(config['sql-prod'])
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    cur = conn.cursor()
    psycopg2.extras.execute_batch(cur, insert_stmt, data.values)
    conn.commit()
    cur.close()
    conn.close()

def get_data(data_path):
    df = pd.read_excel(data_path)
    df = df[['make','model','year']]
    df['year'] = df.year.fillna(2023).astype(int)
    df = df.rename(columns={'model':'brand'})
    df = df.drop_duplicates().reset_index(drop=True)
    df['id'] = df.index
    df.columns = ['car_' + i for i in df.columns]
    df = df[['car_id','car_make','car_brand','car_year']]
    return df

def main(conf_path: str,data_path:str):
    #main
    start_time = time.time()
    if conf_path is None:
        raise ValueError("Arguments missing: conf_path: str, date:str")

    config = get_confg(conf_path)

    data = get_data(data_path)
    push_to_sql(data, config)
    time_taken   = time.time() - start_time
    print('Time taken = {} s'.format(round(time_taken,1)))

#/Users/suraj/Documents/used_car/app/data/Cars.csv
#app/data/Cars.csv
#app/data/Cars.csv
if __name__ == '__main__':
    main(*sys.argv[1:])