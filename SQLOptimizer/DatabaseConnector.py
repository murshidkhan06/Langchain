import mysql.connector
from sqlalchemy import create_engine

class DatabaseConnector:
    def __init__(self, db_type='mysql', **kwargs):
        self.db_type = db_type
        self.connection_params = kwargs

    def get_connection(self):
        if self.db_type == 'mysql':
            return mysql.connector.connect(**self.connection_params)
        elif self.db_type == 'oracle':
            # Add Oracle connection logic here
            pass
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def execute_query(self, query):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result