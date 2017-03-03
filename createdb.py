import psycopg2
from config import config
"""  voir explications
	http://www.postgresqltutorial.com/postgresql-python/create-tables/
		"""



def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE relations (
            relation_id INTEGER PRIMARY KEY ,
            relation_name VARCHAR(255) ,
            is_client BOOLEAN ,
            is_supplier BOOLEAN
        )
        """,
        """ CREATE TABLE sales (
                sale_id INTEGER PRIMARY KEY ,
                relation_id INTEGER
                )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
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
    create_tables()


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79
