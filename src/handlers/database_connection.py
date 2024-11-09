import psycopg2

DATABASE_URL = "postgresql://admin:admin123@postgres:5432/truevoice"

def get_db_connection():
    connection = psycopg2.connect(DATABASE_URL)
    connection.cursor().execute("SET search_path TO truevoice")
    return connection