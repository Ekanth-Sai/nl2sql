from src.nl_to_sql import get_sql_from_natural_language 
from src.db_manager import execute_query, get_all_table_names, connect_db

def display_main_menu():
    #print("Welcome to the Natural Language to SQL Conversion Chatbot.")
    print("Select an option: ")
    print("1. Convert Natural Language to SQL and Execte")
    # print("2. Give the Graphical Interpretation") will define a function for this later for implementation
    print("3. Exit the Application")

def handle_nl_to_sql_flow():
    print("\n---------------------------------------------------")
    print("You've selected 'Convert Natural Language to SQL'.")
    print("---------------------------------------------------")

    while True:
        user_query = input("Enter your Natural Language Query")

        print("Converting Natural Language Query to SQL... ")
        sql_query = get_sql_from_natural_language(user_query)

        if sql_query:
            print(f"Generated SQL query is: {sql_query}")
            confirm = input("Execute this query? (y/n): ").lower()

            if confirm == 'y':
                print("Executing SQL query...")
                results = execute_query(sql_query, fetch_results = True)

                if results is False:
                    print("SQL Query Execution failed")
                elif results is True:
                    print("SQL query executed succesfully")
                elif results is not None:
                    if len(results) > 0:
                        print("Query Results: ")

                        if isinstance(results[0], dict):
                            headers = list(results[0].keys())
                            print(" | ".join(headers))
                            print("-" * (sum(len(str(h)) for h in headers) + 3 * (len(headers) - 1)))

                            for row in results:
                                row_values = [str(row[h]) for h in headers]
                                print(" | ".join(row_values))
                        else:
                            for row in results:
                                print(row)
                        print(f"Found {len(results)} rows")
                    else:
                        print("Query executed successfully, but no rows returned (empty result set).")
                else:
                    print("SQL query executed, but no actionable results were processed.")
            else:
                print("SQL Query Execution Skipped. ")
        else:
            print("Could not generate a valid SQL query from your input.")
            print("Please try rephrasing your question or check the Gemini API configuration.")
        
        continue_nl2sql = input("Do you want to continue with Natural Language to SQL? (y/n): ").lower()
        if continue_nl2sql != 'y':
            print("Returning to Main Menu")
            break

def main():
    print("Hello! I am your SQL chatbot assistant")

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
        display_main_menu()
        choice = input("Your Choide: ").lower()

        if choice == '1':
            handle_nl_to_sql_flow()
        elif choice == '2':
            print("Still in development")
        elif choice == '3':
            print("Exiting Application. Goodbye")
            break
        else:
            print("Invalid choice. ")

if __name__ == "__main__":
    main()
