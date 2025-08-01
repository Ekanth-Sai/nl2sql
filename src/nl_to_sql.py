import google.generativeai as genai 
from google.api_core.exceptions import InternalServerError, GoogleAPICallError 
from .config import GOOGLE_API_KEY
from .db_manager import get_full_schema_for_gemini 

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('models/gemini-2.5-pro')

def get_sql_from_natural_language(natural_language_query):
    if not GOOGLE_API_KEY:
        print("Error: Problem with the API key. Check .env file")
        return None
    
    db_schema = get_full_schema_for_gemini()

    if not db_schema:
        print("Error: Could not retrieve database schema. Cannot generate SQL")
        return None
    
    prompt = f"""You are an AI assistant that converts natural language questions into MySQL SQL queries. You will be provided with the database schema below. Your task is to generate the SQL query that answers the natural language question. Do NOT include any explanations, comments, or additional text in your response, just the SQL query. Ensure the SQL query is syntactically correct for MySQL.
    
    Database Schema:
    {db_schema}

    Natural Language Question:
    "{natural_language_query}"
    
    SQL Query:
    """

    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()

        if sql_query.startswith("```sql") and sql_query.endswith("```"):
            sql_query = sql_query[len("```sql"):-len("```")].strip()
        elif sql_query.startswith("```") and sql_query.endswith("```"):
            sql_query = sql_query[len("```"):-len("```")].strip()

        return sql_query

    except (InternalServerError, GoogleAPICallError) as e:  
        print(f"Gemini API Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during NL to SQL conversion: {e}")
        return None 
