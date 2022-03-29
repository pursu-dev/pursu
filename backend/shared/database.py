'''
Database configuration information
'''
import psycopg2

class DatabaseConfig():
    '''
    Cofiguration for database instance
    '''
    def __init__(self, config):
        self.config = config
        self.conn = self.get_db()

    def get_db(self):
        '''
        Function to obtain psql database connection
        '''
        host, user, password, port, dbname = \
            self.config.DATABASE_HOST, \
            self.config.DATABASE_USERNAME, \
            self.config.DATABASE_PASSWORD, \
            self.config.DATABASE_PORT, \
            self.config.DATABASE_NAME
        conn = None
        try:
            conn = psycopg2.connect(host=host,
                                    user=user,
                                    password=password,
                                    port=port,
                                    dbname=dbname,
                                    keepalives=1,
                                    keepalives_idle=5,
                                    keepalives_interval=2,
                                    keepalives_count=2
                                   )
        except psycopg2.DatabaseError as err:
            print('psycopg2 error:', err)
        return conn

    def execute_query(self, query, cursor):
        '''
        Exception-safe query execution
        '''
        try:
            cursor.execute(query)
            return True
        except psycopg2.Error as err:
            print("DATABASE ERROR: {}. Refreshing connection.".format(err))
            self.conn.rollback()
            cursor.close()
            try:
                cursor = self.refresh_conn()
                cursor.execute(query)
                return True
            except psycopg2.Error as err:
                print("DATABASE ERROR: {}. Skipping transaction.".format(err))
                self.conn.rollback()
                cursor.close()
            return False

    def execute_select_query(self, query):
        '''
        Function to execute a select query.
        '''
        cur = self.refresh_conn()
        output = []
        if self.execute_query(query, cur):
            output = list(cur.fetchall())
            cur.close()
        return output


    def execute_insert_query(self, query):
        '''
        Function to execute an insert query.
        '''
        cur = self.refresh_conn()
        if self.execute_query(query, cur):
            self.conn.commit()
            cur.close()


    def execute_insert_return_query(self, query):
        '''
        Function to execute an insert query that returns inserted field
        '''
        cur = self.refresh_conn()
        return_id = None
        if self.execute_query(query, cur):
            ret = cur.fetchone()
            return_id = ret[0] if len(ret) > 0 else None
            self.conn.commit()
            cur.close()
        return return_id


    def execute_update_query(self, query):
        '''
        Function to execute an update query.
        '''
        cur = self.refresh_conn()
        updated_rows = 0
        if self.execute_query(query, cur):
            updated_rows = cur.rowcount
            self.conn.commit()
            cur.close()
        return updated_rows


    def execute_delete_query(self, query):
        '''
        Function to execute a delete query.
        '''
        cur = self.refresh_conn()
        if self.execute_query(query, cur):
            self.conn.commit()
            cur.close()


    def refresh_conn(self):
        '''
        Refreshes the connection if it is closed or broken.
        '''
        if self.conn.closed != 0:
            self.conn = self.get_db()
        return self.conn.cursor()
    