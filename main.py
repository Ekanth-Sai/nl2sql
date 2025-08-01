from src.nl_to_sql import get_sql_from_natural_language
from src.db_manager import execute_query, get_connection, get_all_table_names
from src.chart_instructor import extract_chart_details
from src.llm_wrapper import gemini_generate_json
from src.chart_generator import generate_chart_from_instruction
import pandas as pd
import os
import time
import webbrowser

def connect_db():
    """Wrapper function for compatibility"""
    return get_connection()

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
                        
                        # Add chart generation option here
                        create_chart = input("\nWould you like to create a chart from these results? (y/n): ").lower()
                        if create_chart == 'y':
                            generate_chart_from_sql_results(results, user_query)
                    else:
                        for row in results:
                            print(row)
                else:
                    print("SQL executed, but no results returned.")
        else:
            print("Failed to generate a valid SQL query.")

        if input("\nTry another NL → SQL? (y/n): ").lower() != 'y':
            break

def generate_chart_from_sql_results(results, original_query):
    """Generate chart directly from SQL results"""
    print("\n" + "=" * 50)
    print("CHART GENERATION FROM RESULTS")
    print("=" * 50)
    
    df = pd.DataFrame(results)
    columns = list(df.columns)
    
    print(f"Available columns: {', '.join(columns)}")
    
    # Simple chart type selection
    print("\nChart Types:")
    print("1. Bar Chart")
    print("2. Pie Chart") 
    print("3. Line Chart")
    
    chart_choice = input("Select chart type (1-3): ").strip()
    chart_types = {"1": "bar", "2": "pie", "3": "line"}
    chart_type = chart_types.get(chart_choice, "bar")
    
    # Column selection
    if len(columns) >= 2:
        print(f"\nColumns: {', '.join([f'{i+1}. {col}' for i, col in enumerate(columns)])}")
        
        try:
            x_idx = int(input("Select X-axis column number: ")) - 1
            y_idx = int(input("Select Y-axis column number: ")) - 1
            
            x_col = columns[x_idx]
            y_col = columns[y_idx]
        except (ValueError, IndexError):
            print("Invalid selection, using first two columns")
            x_col = columns[0]
            y_col = columns[1]
    else:
        print("Not enough columns for chart generation")
        return
    
    title = input("Enter chart title (or press Enter for default): ").strip()
    if not title:
        title = f"{chart_type.title()} Chart - {original_query[:50]}..."
    
    # Create chart config
    chart_config = {
        "chart_type": chart_type,
        "x_axis": x_col,
        "y_axis": y_col,
        "title": title
    }
    
    print(f"\nGenerating {chart_type} chart...")
    generate_chart_from_instruction(df, chart_config)
    
    # Ask to open chart
    open_chart = input("Open chart in browser? (y/n): ").lower()
    if open_chart == 'y':
        try:
            chart_path = f"{chart_type}_chart.html"
            abs_path = os.path.abspath(chart_path)
            webbrowser.open(f'file://{abs_path}')
            print("Chart opened in browser!")
        except Exception as e:
            print(f"Could not open browser: {e}")

def handle_nl_to_chart_flow():
    print("\n" + "=" * 60)
    print("NATURAL LANGUAGE TO CHART GENERATION")
    print("=" * 60)

    while True:
        nl_input = input("\nEnter your chart instruction: ")

        print("Extracting chart configuration from your prompt...")
        chart_config = extract_chart_details(nl_input)

        if not chart_config:
            print("Failed to extract chart configuration. Please try again.")
            continue

        print("\nUnderstood Chart Config:")
        for key, val in chart_config.items():
            print(f"🔹 {key}: {val}")

        sql_choice = input("\nType SQL manually or auto-generate? (manual/auto): ").strip().lower()

        if sql_choice == "manual":
            sql_query = input("Enter your SQL query: ")
        else:
            sql_query = get_sql_from_natural_language(nl_input)
            if sql_query:
                print(f"Auto-generated SQL: {sql_query}")
            else:
                print("Failed to generate SQL. Please enter manually:")
                sql_query = input("Enter your SQL query: ")

        results = execute_query(sql_query, fetch_results=True)
        if not results:
            print("Query execution failed or returned no data.")
        else:
            df = pd.DataFrame(results)
            print(f"Data retrieved: {len(df)} rows, {len(df.columns)} columns")
            generate_chart_from_instruction(df, chart_config)
            
            # Ask to open chart
            open_chart = input("Open chart in browser? (y/n): ").lower()
            if open_chart == 'y':
                try:
                    chart_type = chart_config.get("chart_type", "bar")
                    chart_path = f"{chart_type}_chart.html"
                    abs_path = os.path.abspath(chart_path)
                    webbrowser.open(f'file://{abs_path}')
                    print("Chart opened in browser!")
                except Exception as e:
                    print(f"Could not open browser: {e}")

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
