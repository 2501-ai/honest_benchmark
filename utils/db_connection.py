import os
from dotenv import load_dotenv
import psycopg2
import json

class DBConnector:
    def __init__(self, env_path='.env'):
        # Load environment variables from the .env file
        load_dotenv(env_path)

        # Retrieve database connection URL from environment variables
        self.database_url = os.getenv('DATABASE_URL')

        # Establish a connection to the PostgreSQL database during initialization
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(self.database_url)
            print("Connection to PostgreSQL DB successful")
        except Exception as e:
            print(f"Error connecting to PostgreSQL DB: {e}")
            self.connection = None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection closed")

    def store_benchmark_result(self, result_data):
        """
        Store benchmark result in the benchmark_results table.

        :param result_data: Dictionary containing benchmark result fields
        :return: Number of rows inserted or None if failed
        """
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO benchmark_results (task_id, test_name, passed, duration_ms, accuracy, error_message, test)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Serialize JSON fields
            test_json = json.dumps(result_data['test'])

            cursor.execute(query, (
                result_data['task_id'],
                result_data['test_name'],
                result_data['passed'],
                result_data['duration_ms'],
                result_data['accuracy'],
                result_data.get('error_message'),
                test_json
            ))
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error storing benchmark result: {e}")
            self.connection.rollback()
            return None