import psycopg
from config import DB_CONFIG

def get_db_connection():
    return psycopg.connect(**DB_CONFIG)
