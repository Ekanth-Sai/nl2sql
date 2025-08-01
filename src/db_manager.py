import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "nl2sql_user")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "admin")
DB_NAME = os.getenv("MYSQL_DB", "nl_to_sql_db")

def get_full_schema_for_gemini():
    tables = get_all_table_names()
    schema = ""
    for table in tables:
        columns = get_table_schema(table)
        schema += f"Table: {table}\n"
        for col_name, col_type in columns:
            schema += f"  - {col_name}: {col_type}\n"
        schema += "\n"
    return schema.strip()


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def execute_query(query, fetch_results=True):
    connection = get_connection()
    if connection is None:
        print("Could not establish connection")
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)

        if fetch_results and query.strip().upper().startswith("SELECT"):
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            connection.commit()
            return True

    except Error as e:
        print(f"Query execution failed: {e}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_all_table_names():
    connection = get_connection()
    if connection is None:
        print("Could not establish connection")
        return []

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching table names: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_table_schema(table_name):
    connection = get_connection()
    if connection is None:
        print("Could not establish connection")
        return []

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        return [(row[0], row[1]) for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching schema for {table_name}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
