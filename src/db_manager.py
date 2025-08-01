import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "your_database_name")

def get_full_schema_for_gemini():
    """
    Returns the full database schema as a string formatted for LLM input.
    Example:
    Table: users
    - id: INT
    - name: VARCHAR(255)

    Table: orders
    - order_id: INT
    - amount: FLOAT
    """
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
    """
    Always create a fresh DB connection to avoid stale connections across Streamlit reruns.
    """
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
        print(f"❌ Error connecting to MySQL: {e}")
    return None

def execute_query(query, fetch_results=True):
    """
    Execute any SQL query.
    If it's a SELECT, returns list of dicts.
    For INSERT/UPDATE/DELETE, commits the change.
    """
    connection = get_connection()
    if connection is None:
        print("❌ Could not establish connection")
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
        print(f"❌ Query execution failed: {e}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_all_table_names():
    """
    Returns list of all table names in the current DB.
    """
    connection = get_connection()
    if connection is None:
        print("❌ Could not establish connection")
        return []

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"❌ Error fetching table names: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_table_schema(table_name):
    """
    Returns list of (column_name, data_type) for a given table.
    """
    connection = get_connection()
    if connection is None:
        print("❌ Could not establish connection")
        return []

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        return [(row[0], row[1]) for row in cursor.fetchall()]
    except Error as e:
        print(f"❌ Error fetching schema for {table_name}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
