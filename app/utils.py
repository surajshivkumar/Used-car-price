import configparser
import psycopg2
import psycopg2.extras

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
