from src.nl_to_sql import get_sql_from_natural_language 
from src.db_manager import execute_query, get_all_table_names, connect_db

def main():
    conn = connect_db()

    if conn:
        conn.close()
        print("Database connection successful")
    else:
        print("Connection failure")
        return
    
    print("Available tables in the database: ")
    tables = get_all_table_names()

    if tables:
        for table in tables:
            print(f"-{table}")
    else:
        print("No tables found. Check your schema")
    
    print("-" * 30)

    while(True):
        user_query = input("\nEnter your natural language query: ")
        if user_query.lower() == 'exit':
            print("Exiting application. Goodbye!")
            break

        print("\nConverting natural language to SQL...")
        sql_query = get_sql_from_natural_language(user_query)

        if sql_query:
            print(f"Generated SQL Query:\n{sql_query}")
            confirm = input("\nExecute this SQL query? (y/n): ").lower()
            if confirm == 'y':
                print("Executing SQL query...")
                results = execute_query(sql_query, fetch_results=True) # Always try to fetch results

                if results is False: # Check for explicit False indicating an error
                    print("SQL query execution failed.")
                elif results is True: # For non-SELECT queries that returned True (success)
                    print("SQL query executed successfully (no results to display, likely DDL/DML).")
                elif results is not None:
                    if len(results) > 0:
                        print("\nQuery Results:")
                        # Print header
                        if isinstance(results[0], dict):
                            headers = list(results[0].keys())
                            print(" | ".join(headers))
                            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
                            for row in results:
                                row_values = [str(row[h]) for h in headers]
                                print(" | ".join(row_values))
                        else: # Fallback for tuple results if db_manager was changed
                            for row in results:
                                print(row)
                        print(f"\nFound {len(results)} rows.")
                    else:
                        print("Query executed successfully, but no rows returned (empty result set).")
                else: # results is None, implies some internal issue or no results expected/handled
                    print("SQL query executed, but no actionable results were processed.")
            else:
                print("SQL query execution skipped.")
        else:
            print("Could not generate a valid SQL query from your input.")
            print("Please try rephrasing your question or check the Gemini API configuration.")

if __name__ == "__main__":
    main()
