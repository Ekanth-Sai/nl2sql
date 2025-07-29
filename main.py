from src.nl_to_sql import get_sql_from_natural_language 
from src.db_manager import execute_query, get_all_table_names, connect_db
from src.chart_generator import (
    generate_chart_from_query, 
    generate_html_with_chart, 
    smart_chart_suggestion,
    determine_chart_type
)
import os
import webbrowser

def display_main_menu():
    print("Select an option: ")
    print("1. Convert Natural Language to SQL and Execute")
    print("2. Exit the Application")

def handle_nl_to_sql_flow():
    print("\n" + "="*60)
    print("NATURAL LANGUAGE TO SQL CONVERSION")
    print("="*60)

    while True:
        user_query = input("\n Enter your Natural Language Query: ")
        print("Converting Natural Language Query to SQL... ")
        sql_query = get_sql_from_natural_language(user_query)

        if sql_query:
            print(f"Generated SQL query: {sql_query}")
            confirm = input("Execute this query? (y/n): ").lower()

            if confirm == 'y':
                print("Executing SQL query...")
                results = execute_query(sql_query, fetch_results=True)

                if results is False:
                    print("SQL Query Execution failed")
                elif results is True:
                    print("SQL query executed successfully")
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
                        
                        create_chart = input("\nWould you like to create a chart from these results? (y/n): ").lower()
                        if create_chart == 'y':
                            generate_chart_from_results(results, user_query, sql_query)
                    else:
                        print("Query executed successfully, but no rows returned (empty result set).")
                else:
                    print("SQL query executed, but no actionable results were processed.")
            else:
                print("SQL Query Execution Skipped.")
        else:
            print("Could not generate a valid SQL query from your input.")
            print("Please try rephrasing your question or check the Gemini API configuration.")
        
        continue_nl2sql = input("\nDo you want to continue with Natural Language to SQL? (y/n): ").lower()
        if continue_nl2sql != 'y':
            print("Returning to Main Menu")
            break

def generate_chart_from_results(results, natural_language_query, sql_query):
    print("\n" + "="*50)
    print("CHART GENERATION")
    print("="*50)
    
    print("Getting AI suggestions for best chart type...")
    suggested_chart_type, suggested_title = smart_chart_suggestion(natural_language_query, results)
    
    if suggested_chart_type and suggested_title:
        print(f"AI Recommendation:")
        print(f"   Chart Type: {suggested_chart_type.title()} Chart")
        print(f"   Title: {suggested_title}")
        
        use_suggestion = input("\nUse AI recommendation? (y/n): ").lower()
        
        if use_suggestion == 'y':
            chart_type = suggested_chart_type
            title = suggested_title
        else:
            chart_type, title = get_user_chart_preferences()
    else:
        print("Could not get AI suggestions, manual selection required.")
        chart_type, title = get_user_chart_preferences()
    
    print(f"\nGenerating {chart_type.title()} Chart...")
    
    from src.chart_generator import generate_chart_config
    chart_config = generate_chart_config(results, chart_type, title)
    
    if chart_config:
        import time
        timestamp = int(time.time())
        filename = f"chart_{chart_type}_{timestamp}.html"
        
        print("Saving chart...")
        success = generate_html_with_chart(chart_config, filename)
        
        if success:
            print(f"Chart generated successfully: {filename}")
            open_chart = input("Open chart in browser? (y/n): ").lower()
            if open_chart == 'y':
                try:
                    abs_path = os.path.abspath(filename)
                    webbrowser.open(f'file://{abs_path}')
                    print("Chart opened in browser!")
                except Exception as e:
                    print(f"Could not open browser: {e}")
                    print(f"Please manually open: {os.path.abspath(filename)}")
        else:
            print("Failed to generate chart HTML file")
    else:
        print("Failed to generate chart configuration")
    
    print("\n" + "="*50)

def get_user_chart_preferences():
    print("\nAvailable chart types:")
    print("   1. Pie Chart - Best for showing proportions/percentages")
    print("   2. Bar Chart - Best for comparing categories")
    print("   3. Histogram - Best for showing data distribution")
    
    while True:
        choice = input("\nSelect chart type (1-3): ").strip()
        if choice == '1':
            chart_type = 'pie'
            break
        elif choice == '2':
            chart_type = 'bar'
            break
        elif choice == '3':
            chart_type = 'histogram'
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
    
    title = input("Enter chart title (or press Enter for default): ").strip()
    if not title:
        title = "Data Visualization"
    
    return chart_type, title

def main():
    print("Hello! I am your SQL chatbot assistant with visualization capabilities")

    conn = connect_db()

    if conn:
        conn.close()
        print("Database connection successful")
    else:
        print("Connection failure")
        return
    
    print("\nAvailable tables in the database: ")
    tables = get_all_table_names()

    if tables:
        for table in tables:
            print(f"   • {table}")
    else:
        print("No tables found. Check your schema")
    
    print("=" * 50)

    while True:
        display_main_menu()
        choice = input("Your Choice: ").strip()

        if choice == '1':
            handle_nl_to_sql_flow()
        elif choice == '2':
            print("Exiting Application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()
