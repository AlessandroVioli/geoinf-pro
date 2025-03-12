import pandas as pd
import psycopg2
import psycopg2.extras as extras 

# default
DB_URL = 'postgresql://postgres:ele1234567@localhost:5432/olulcmaps_dev'
CONN_INFO = {
    "database": "olulcmaps_dev", 
    "user": 'postgres', 
    "password": 'ele1234567', 
    "host": '127.0.0.1', 
    "port": '5432'
}
def batch_import(df, table, conn_info=CONN_INFO):
    conn = psycopg2.connect(**conn_info)
    # creating a cursor 
    cursor = conn.cursor() 
    tuples = [tuple(x) for x in df.to_numpy()] 
    cols = ','.join(list(df.columns))
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols) 
    cursor = conn.cursor() 
    try: 
        extras.execute_values(cursor, query, tuples) 
        conn.commit() 
    except (Exception, psycopg2.DatabaseError) as error: 
        print("Error: %s" % error) 
        conn.rollback() 
        cursor.close() 
        return 1
    print("execute_values() done") 
    cursor.close() 

def batch_update(df, table, conn_info=CONN_INFO):
    conn = psycopg2.connect(**conn_info)
    # creating a cursor 
    cursor = conn.cursor() 
    tuples = [tuple(x) for x in df.to_numpy()] 
    cols = ','.join(list(df.columns))
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols) 
    cursor = conn.cursor() 
    try: 
        extras.execute_values(cursor, query, tuples) 
        conn.commit() 
    except (Exception, psycopg2.DatabaseError) as error: 
        print("Error: %s" % error) 
        conn.rollback() 
        cursor.close() 
        return 1
    print("execute_values() done") 
    cursor.close() 


def batch_import_lulc_map_downloads(csv_path):    
    df = pd.read_csv(csv_path)
    table_name = 'lulc_map_downloads'
    batch_import(df, table_name)


if __name__ == '__main__':
    #csv_path=r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/GFC.csv"
    #csv_path = r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/ESA WorldCover 10 m 2021 v200.csv"
    #csv_path = r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/GWL_FCS30D.csv"
    #csv_path = r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/GISD30.csv"
    csv_path = r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/GLC_FCS30D.csv"
    batch_import_lulc_map_downloads(csv_path)
