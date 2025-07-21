import mysql.connector 
from mysql.connector import Error 
from .config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def connect_db():
    try:
        connection = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASSWORD,
            database = DB_NAME
        )

        if connection.is_connected():
            print("Connected to db successfully")
            return connection
        
    except Error as e:
        print(f"Error connecting to db: {e}")
        return None
    
def execute_query(query, fetch_results = True):
    connection = None
    cursor = None 

    try:
        connection = connect_db()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        cursor.execute(query)

        if fetch_results and query.strip().upper().statswith("SELECT"):
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            dict_results = []

            for row in results:
                dict_results.append(dict(zip(columns, row)))
            return dict_results
        else:
            connection.commit()
            print("Query executed succesfully")
            return True
        
    except Error as e:
        print(f"Error executing query: {e}")

        if connection:
            connection.rollback()
        return False 
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")

def get_table_schema(table_name):
    query = f"DESCRIBE {table_name};"
    connection = None
    cursor = None 
    schema_str = ""

    try:
        connection = connect_db()

        if connection is None:
            return None 
        
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            schema_str += f"Table: {table_name}\n"
            schema_str += "Columns: \n"

            for col in results:
                columns_name = col[0]
                column_type = col[1]
                schema_str += f"-{columns_name} ({column_type})\n"

            return schema_str
        else:
            print(f"Table '{table_name}' not found or no columns retrieved")
            return None 
    except Error as e:
        print(f"Error fetching schema for table '{table_name}': {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_all_table_names():
    query = "SHOW TABLES;"
    connection = None
    cursor = None 
    table_names = []

    try:
        connection = connect_db()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            table_names.append(row[0])

        return table_names
    except Error as e:
        print(f"Error fetching table names: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_full_schema_for_gemini():
    all_table_names = get_all_table_names()

    if not all_table_names:
        print("Could not retrieve any table names. Please check database connection and permissions")
        return ""

    full_schema_string = "MySQL Database Schema: \n"

    for table_name in all_table_names:
        schema_info =  get_table_schema(table_name)
        if schema_info:
            full_schema_string += "\n" + schema_info
    
    return full_schema_string