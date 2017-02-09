import os
import psycopg2
import configparser
from psycopg2.extras import DictCursor

""" etablir connection POSTGRES """

config = configparser.ConfigParser()


with open('db_psql.cfg') as configfile:
    config.read('db_psql.cfg')	

for key in config['PRUNELLE'] :  print(key,config['PRUNELLE'][key])
print(config)

conn = psycopg2.connect("dbname=  user= host=  password=  ")
print(type(conn))

cursor = conn.cursor()
print(type(cursor))
cursor.execute("CREATE TABLE element ( numero INTEGER, nom VARCHAR(40), colonne INTEGER, ligne INTEGER);")
cursor.execute("""INSERT INTO element ( numero, nom, colonne, ligne) VALUES
        (1,'HYROGENNE',1,1),
        (2, 'HELUIM',1,1)
        """)
print(" nbre de colonne inseres : %d" % cursor.rowcount)
cursor.close()
cursor1 = conn.cursor(cursor_factory=DictCursor)
cursor1.execute('select * from element')
results = cursor1.fetchall()
print(type(results))
print(type(results[0]))
print(results)
