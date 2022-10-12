import psycopg2
from psycopg2 import Error


class DB:
    def __init__(self, user, password, db_name, host="127.0.0.1", port="5432"):
        self.connection = None
        self.connect_db(user, password, db_name, host, port)

    def connect_db(self, user, password, db_name, host="127.0.0.1", port="5432"):
        try:
            # Connect to an existing database
            self.connection = psycopg2.connect(user=user,
                                               password=password,
                                               host=host,
                                               port=port,
                                               database=db_name)

            # Create a cursor to perform database operations
            self.cursor = self.connection.cursor()
            # Executing a SQL query
            self.cursor.execute("SELECT version();")
            # Fetch result
            record = self.cursor.fetchone()
            print("You are connected to - ", record, "\n")
            return self.cursor

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
            return None

    def run_query(self, query, **kwargs):
        self.cursor.execute(query, kwargs)
        try:
            return self.cursor.fetchall()
        except Exception as e:
            return None

    def disconnect_db(self):
        if self.connection:
            self.connection.close()
            self.connection.close()
            print("PostgreSQL connection is closed")
