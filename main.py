from src.nl_to_sql import get_sql_from_natural_language
from src.db_manager import execute_query, get_connection, get_all_table_names, get_table_schema
from src.chart_generator import generate_chart_from_instruction, get_chart_suggestions
import pandas as pd
import os
import webbrowser

def display_main_menu():
    print("\n" + "=" * 60)
    print("🚀 NL2SQL + CHART GENERATOR")
    print("=" * 60)
    print("1. Natural Language → SQL → Chart")
    print("2. View Database Schema")
    print("3. Exit")

def show_sample_queries():
    """Display sample queries to help users"""
    samples = [
        "Show me all records from the first table",
        "What is the total count by category?",
        "Find the top 5 records by some numeric value",
        "How many records are there in each table?",
        "Show me the average values grouped by some column"
    ]
    
    print("\n💡 Sample queries you can try:")
    for i, query in enumerate(samples, 1):
        print(f"   {i}. {query}")

def display_database_info():
    """Display database schema information"""
    print("\n" + "=" * 60)
    print("📊 DATABASE SCHEMA")
    print("=" * 60)
    
    tables = get_all_table_names()
    if not tables:
        print("❌ No tables found or connection failed")
        return
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        schema = get_table_schema(table)
        if schema:
            for col_name, col_type in schema:
                print(f"   • {col_name}: {col_type}")
        else:
            print("   ❌ Could not fetch schema")

def handle_chart_generation(results, original_query):
    """Enhanced chart generation with smart suggestions"""
    if not results:
        print("❌ No data available for chart generation")
        return
    
    print("\n" + "=" * 60)
    print("📊 CHART GENERATION")
    print("=" * 60)
    
    df = pd.DataFrame(results)
    columns = list(df.columns)
    
    print(f"📋 Available columns: {', '.join(columns)}")
    print(f"📈 Data shape: {len(df)} rows, {len(df.columns)} columns")
    
    # Get intelligent chart suggestions
    suggestions = get_chart_suggestions(df)
    
    if suggestions:
        print("\n💡 Smart chart suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            reason = suggestion.get('reason', '')
            print(f"   {i}. {suggestion['type'].title()} Chart: {suggestion['x']} vs {suggestion.get('y', 'N/A')} ({reason})")
        
        use_suggestion = input("\nUse a suggested chart? (y/n): ").lower()
        if use_suggestion == 'y':
            try:
                choice = int(input("Select suggestion number: ")) - 1
                if 0 <= choice < len(suggestions):
                    suggestion = suggestions[choice]
                    config = {
                        "chart_type": suggestion['type'],
                        "x_axis": suggestion['x'],
                        "y_axis": suggestion.get('y'),
                        "title": f"{suggestion['type'].title()} Chart - {original_query[:50]}..."
                    }
                    
                    print(f"\n🎨 Generating {suggestion['type']} chart...")
                    if generate_chart_from_instruction(df, config):
                        open_chart_in_browser(config["chart_type"])
                    return
            except (ValueError, IndexError):
                print("❌ Invalid selection, continuing with manual setup...")
    
    # Manual chart configuration
    print("\n🎨 Available Chart Types:")
    chart_types = ["bar", "pie", "line", "scatter", "histogram"]
    for i, chart_type in enumerate(chart_types, 1):
        print(f"   {i}. {chart_type.title()} Chart")
    
    try:
        chart_choice = int(input("Select chart type (1-5): ")) - 1
        chart_type = chart_types[chart_choice]
    except (ValueError, IndexError):
        print("❌ Invalid selection, using bar chart")
        chart_type = "bar"
    
    # Column selection
    if len(columns) >= 2:
        print(f"\n📊 Available Columns:")
        for i, col in enumerate(columns, 1):
            # Show data type info
            dtype = str(df[col].dtype)
            print(f"   {i}. {col} ({dtype})")
        
        try:
            x_idx = int(input("Select X-axis column: ")) - 1
            x_col = columns[x_idx]
            
            if chart_type != "histogram":
                y_idx = int(input("Select Y-axis column: ")) - 1
                y_col = columns[y_idx]
            else:
                y_col = None
                
        except (ValueError, IndexError):
            print("❌ Invalid selection, using first two columns")
            x_col = columns[0]
            y_col = columns[1] if len(columns) > 1 and chart_type != "histogram" else None
    else:
        print("❌ Not enough columns for chart generation")
        return
    
    title = input("Enter chart title (or press Enter for default): ").strip()
    if not title:
        title = f"{chart_type.title()} Chart - {original_query[:50]}..."
    
    config = {
        "chart_type": chart_type,
        "x_axis": x_col,
        "y_axis": y_col,
        "title": title
    }
    
    print(f"\n🎨 Generating {chart_type} chart...")
    if generate_chart_from_instruction(df, config):
        open_chart_in_browser(chart_type)

def open_chart_in_browser(chart_type):
    """Helper function to open chart in browser"""
    open_chart = input("🌐 Open chart in browser? (y/n): ").lower()
    if open_chart == 'y':
        try:
            chart_path = f"{chart_type}_chart.html"
            if os.path.exists(chart_path):
                abs_path = os.path.abspath(chart_path)
                webbrowser.open(f'file://{abs_path}')
                print("✅ Chart opened in browser!")
            else:
                print("❌ Chart file not found")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")

def handle_nl_to_sql_flow():
    print("\n" + "=" * 60)
    print("🔄 NATURAL LANGUAGE TO SQL CONVERSION")
    print("=" * 60)
    
    show_sample_queries()

    while True:
        user_query = input("\n💭 Enter your Natural Language Query: ").strip()
        
        if not user_query:
            print("❌ Query cannot be empty")
            continue
            
        print("🔄 Converting to SQL...")
        sql_query = get_sql_from_natural_language(user_query)

        if not sql_query:
            print("❌ Failed to generate a valid SQL query")
            retry = input("🔄 Try again? (y/n): ").lower()
            if retry != 'y':
                break
            continue

        print(f"\n📝 Generated SQL:")
        print("-" * 50)
        print(sql_query)
        print("-" * 50)
        
        confirm = input("✅ Execute this query? (y/n): ").lower()
        if confirm != 'y':
            print("Query not executed.")
            continue

        print("⚡ Executing query...")
        results = execute_query(sql_query, fetch_results=True)
        
        if results is False:
            print("❌ SQL Execution failed")
        elif results is True:
            print("✅ SQL executed successfully (no output)")
        elif results:
            print(f"\n📊 Query Results ({len(results)} rows):")
            print("=" * 80)
            
            # Display results in a nice format
            if isinstance(results[0], dict):
                headers = list(results[0].keys())
                
                # Print headers
                header_line = " | ".join([f"{h:>15}" for h in headers])
                print(header_line)
                print("-" * len(header_line))
                
                # Print rows (limit to first 10 for readability)
                display_rows = results[:10]
                for row in display_rows:
                    row_line = " | ".join([f"{str(row[col])[:15]:>15}" for col in headers])
                    print(row_line)
                
                if len(results) > 10:
                    print(f"... and {len(results) - 10} more rows")
                
                print("=" * 80)
                
                # Offer chart generation
                create_chart = input("\n📊 Create a chart from these results? (y/n): ").lower()
                if create_chart == 'y':
                    handle_chart_generation(results, user_query)
            else:
                for row in results:
                    print(row)
        else:
            print("✅ SQL executed, but no results returned")

        if input("\n🔄 Try another query? (y/n): ").lower() != 'y':
            break

def main():
    print("🎉 Welcome to NL2SQL + Chart Generator!")
    print("Transform your questions into SQL queries and beautiful charts!")

    # Test database connection
    print("\n🔌 Testing database connection...")
    conn = get_connection()
    if conn:
        conn.close()
        print("✅ Database connection successful")
    else:
        print("❌ Failed to connect to database")
        print("💡 Please check your .env file and database configuration")
        return

    # Show available tables
    print("\n📋 Available Tables:")
    tables = get_all_table_names()
    if tables:
        for table in tables:
            print(f"   • {table}")
    else:
        print("   ❌ No tables found in database")

    while True:
        display_main_menu()
        choice = input("\n🎯 Your Choice: ").strip()

        if choice == '1':
            handle_nl_to_sql_flow()
        elif choice == '2':
            display_database_info()
        elif choice == '3':
            print("👋 Thank you for using NL2SQL + Chart Generator!")
            print("Goodbye! 🚀")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()