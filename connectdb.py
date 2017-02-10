#!/usr/bin/python

import psycopg2
from config import config


""" etablir connection POSTGRES """

def connect():
    """ connect a la base PostgreSQL """
    conn = None
    try :
        # lire les paramete de connection
        params = config()
        print(params)        
        # connection au serveur
        print(' connection au serveur Postgres  ....')
        conn = psycopg2.connect(**params)

        # creer un curseur 
        cur = conn.cursor()

        # exectuter un ordre
        print('PostgresSQL base de donne version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)

        # fermer la connection
        cur.close
    except (Exception, psycopg2.DatabaseError) as error :
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print(' connexion a la base fermé ')

if __name__ == '__main__':
    connect()


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79
