import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD'])

    return conn