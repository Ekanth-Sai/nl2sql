import os
from dotenv import load_dotenv 

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "nl2sql_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_NAME = os.getenv("DB_NAME", "nl_to_sql_db")

