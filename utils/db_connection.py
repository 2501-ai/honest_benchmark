import json
import os

import psycopg2
from dotenv import load_dotenv


class DBConnector:
    def __init__(self, env_path='.env'):
        # Load environment variables from the .env file
        load_dotenv(env_path)

        # Retrieve database connection URL from environment variables
        self.database_url = os.getenv('DIRECT_URL')
        if not self.database_url:
            raise ValueError("Database 'DIRECT_URL' not found in environment variables")

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
            INSERT INTO "Benchmarks" (task_id, task_name, benchmark_id, input, labels, passed, duration_ms, pre_process_model, model_pair, accuracy, run_at, benchmark_file, error_message, test)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Serialize JSON fields
            test_json = json.dumps(result_data['test'])
            labels_json = json.dumps(result_data['labels'])
            model_pair_json = json.dumps(result_data['model_pair'])

            arguments = (
                result_data['task_id'],
                result_data['task_name'],
                result_data['benchmark_id'],
                result_data['input'],
                labels_json,
                result_data['passed'],
                result_data['duration_ms'],
                result_data['pre_process_model'],
                model_pair_json,
                result_data['accuracy'],
                result_data['run_at'],
                result_data['benchmark_file'],
                result_data['error_message'],
                test_json
            )

            cursor.execute(query, arguments)

            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error storing benchmark result: {e}")

            self.connection.rollback()
            return None
