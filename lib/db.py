import psycopg2
from psycopg2 import Error, extras



class DB:
    def __init__(self, user, password, db_name, host="127.0.0.1", port="5432"):
        self.cursor = None
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
            self.connection.autocommit = True
            # Create a cursor to perform database operations
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Executing a SQL query
            self.cursor.execute("SELECT version();")
            # Fetch result
            record = self.cursor.fetchone()
            print("You are connected to - ", record, "\n")
            return self.cursor

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
            return None

    def run_query(self, query, *args):
        self.cursor.execute(query, args)
        try:
            return self.cursor.fetchall()
        except Exception as e:
            return None

    def disconnect_db(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")

    def __del__(self):
        self.disconnect_db()


# DB_NAME = "stock_trade"
# DB_USER = "admin"
# DB_PASS = "admin"
# db_obj = DB(DB_USER, DB_PASS, DB_NAME)
# user = db_obj.run_query("SELECT * FROM users WHERE email ='sample@gmail.com'")
# print(user["id"])