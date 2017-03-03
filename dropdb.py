import psycopg2
from config import config




def drop_tables():
    """ drop tables in the PostgreSQL database"""
    commands = (
        """
        DROP DATABASE relations 
        
        """,
        """ DROP DATABASE sales 
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        conn.set_isolation_level(0)
        # drop table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    drop_tables()


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79
