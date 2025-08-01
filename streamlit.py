import streamlit as st
from src.nl_to_sql import get_sql_from_natural_language
from src.db_manager import execute_query
from src.chart_generator import determine_chart_type
import pandas as pd
import plotly.express as px

st.set_page_config(page_title = "NL2SQL Chatbot", layout = "wide")

st.title("NL2SQL Chatbot and Visualization")
st.markdown("Ask questions in plain English. Get SQL and charts")

user_query = st.chat_input("Ask a question in Natural Language...")

if "history" not in st.session_state:
    st.session_state.history = []

if user_query:
    st.session_state.history.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking...Generating the SQL Query..."):
            sql = get_sql_from_natural_language(user_query)
        
        if sql: 
            st.markdown(f"**SQL Generated:**\n```sql\n{sql}\n```")

            results = execute_query(sql, fetch_results = True)
            if results and isinstance(results, list) and len(results) > 0:
                df = pd.DataFrame(results)
                st.success(f"Query Succesful - {len(df)} rows fetched")
                st.dataframe(df)

                with st.expander("Generate chart", expanded = True):
                    chart_type = st.selectbox("Select chart type", ["Auto", "Pie", "Bar", "Histogram"])
                    chart_title = st.text_input("Chart Title", "Data Visualization")

                    if st.button("Generate Chart"):
                        if chart_type == "Auto":
                            chart_type = determine_chart_type(results)
                        
                        fig = generate_plotly_chart(df, chart_type.lower(), chart_title)

                        if fig:
                            st.plotly_chart(fig, use_container_width = True)
                        else:
                            st.error("Could not generate chart with selected type")
            else:
                st.warning("Query returned no results or failed")
        else:
            st.error("Gemeini failed to generate a valid sql query")           

def generate_plotly_chart(df, chart_type, title):
    if df.shape[1] < 1:
        return None
    
    try:
        if chart_type == "pie" and df.shape[1] >= 2:
            return px.pie(df, names = df.columns[0], values = df.columns[1], title = title)
        elif chart_type == "bar" and df.shape[1] >= 2:
            return px.bar(df, x = df.columns[0], y = df.columns[1], title = title)
        elif chart_type == "histogram":
            numeric_cols = df.select_dtypes(include = ['number']).columns
            if len(numeric_cols) > 0:
                return px.histogram(df, x = numeric_cols[0], title = title)
    except Exception as e:
        st.error(f"Chart generation error: {e}")
        return None