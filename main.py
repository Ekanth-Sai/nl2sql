from src.nl_to_sql import get_sql_from_natural_language
from src.db_manager import execute_query
from src.chart_instructor import extract_chart_details
from src.llm_wrapper import gemini_generate_json
from src.chart_generator import generate_chart_from_instruction
import pandas as pd
import os
import time
import webbrowser

def display_main_menu():
    print("\n" + "=" * 50)
    print("MAIN MENU")
    print("=" * 50)
    print("1. Natural Language → SQL Execution")
    print("2. Natural Language → Chart Generation")
    print("3. Exit")

def handle_nl_to_sql_flow():
    print("\n" + "=" * 60)
    print("NATURAL LANGUAGE TO SQL CONVERSION")
    print("=" * 60)

    while True:
        user_query = input("\nEnter your Natural Language Query: ")
        print("Converting to SQL...")
        sql_query = get_sql_from_natural_language(user_query)

        if sql_query:
            print(f"Generated SQL: {sql_query}")
            confirm = input("Execute this query? (y/n): ").lower()

            if confirm == 'y':
                results = execute_query(sql_query, fetch_results=True)
                if results is False:
                    print("SQL Execution failed.")
                elif results is True:
                    print("SQL executed successfully (no output).")
                elif results:
                    print("\nQuery Results:")
                    if isinstance(results[0], dict):
                        headers = list(results[0].keys())
                        print(" | ".join(headers))
                        print("-" * (len(" | ".join(headers))))

                        for row in results:
                            print(" | ".join([str(row[col]) for col in headers]))
                        print(f"\nReturned {len(results)} rows.")
                    else:
                        for row in results:
                            print(row)
                else:
                    print("SQL executed, but no results returned.")
        else:
            print("Failed to generate a valid SQL query.")

        if input("\nTry another NL → SQL? (y/n): ").lower() != 'y':
            break

def handle_nl_to_chart_flow():
    print("\n" + "=" * 60)
    print("NATURAL LANGUAGE TO CHART GENERATION")
    print("=" * 60)

    while True:
        nl_input = input("\nEnter your chart instruction: ")

        print("Extracting chart configuration from your prompt...")
        chart_config = extract_chart_details(nl_input)

        print("\nUnderstood Chart Config:")
        for key, val in chart_config.items():
            print(f"🔹 {key}: {val}")

        sql_choice = input("\nType SQL manually or auto-generate? (manual/auto): ").strip().lower()

        if sql_choice == "manual":
            sql_query = input("Enter your SQL query: ")
        else:
            sql_query = get_sql_from_natural_language(nl_input)
            print(f"Auto-generated SQL: {sql_query}")

        results = execute_query(sql_query, fetch_results=True)
        if not results:
            print("Query execution failed or returned no data.")
        else:
            df = pd.DataFrame(results)
            generate_chart_from_instruction(df, chart_config)

        if input("\nCreate another chart? (y/n): ").lower() != 'y':
            break

def main():
    print("Welcome to NL2SQL + NL2Chart CLI Assistant!")

    conn = connect_db()
    if conn:
        conn.close()
        print("Database connection successful.")
    else:
        print("Failed to connect to database.")
        return

    print("\nAvailable Tables:")
    tables = get_all_table_names()
    if tables:
        for table in tables:
            print(f"   • {table}")
    else:
        print("No tables found in schema.")

    while True:
        display_main_menu()
        choice = input("Your Choice: ").strip()

        if choice == '1':
            handle_nl_to_sql_flow()
        elif choice == '2':
            handle_nl_to_chart_flow()
        elif choice == '3':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
