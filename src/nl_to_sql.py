import google.generativeai as genai 
import google.api_core.exceptions
from .config import GOOGLE_API_KEY
from .db_manager import get_full_schema_for_gemini 

genai.configure(api_key = GOOGLE_API_KEY)

model = genai.GenerativeModel('models/gemini-2.5-pro')

def get_sql_from_natural_language(natural_language_query):
    if not GOOGLE_API_KEY:
        print("Error: Problem with the API key. Check .env file")
        return None
    
    db_schema = get_full_schema_for_gemini()

    if not db_schema:
        print("Error: Could not retrieve database schema. Cannot geenrate SQL")
        return None
    
    prompt = f"""You are an AI assistant that converts natural language questions into MySQL SQL queries. You will be provided with the database schema below.Your task is to generate the SQL query that answers the natural language question.Do NOT include any explanations, comments, or additional text in your response, just the SQL query.Ensure the SQL query is syntactically correct for MySQL.
    
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
    except genai.APIError as e:
        print(f"Gemini API Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occured during NL to SQL conversion: {e}")
        return None 

if __name__ == "__main__":
    print("Beginning of testing module")

    test_queries = [
        "How many claims are there in total?",
        "Show me the top 5 claim statuses and their counts.",
        "What is the total amount paid by the plan for pharmacy claims?",
        "List all medical claims for patients in California.",
        "Find the average total charges for claims with 'Illness' as the claim cause."
    ]

    for query in test_queries:
        print(f"\nNatural Language Query: {query}")
        sql_output = get_sql_from_natural_language(query)

        if sql_output:
            print(f"Generated SQL: \n{sql_output}")
        else:
            print("Failed to generate SQL")
    
    print("End of testing module")

    