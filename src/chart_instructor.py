from src.llm_wrapper import gemini_generate_json

def extract_chart_details(nl_instruction):
    prompt = f"""
You're a chart-building assistant. Convert this instruction into chart config JSON:
"{nl_instruction}"

Respond in:
{{
    "chart_type": "bar",
    "x_axis": "department",
    "y_axis": "user_count",
    "color": "red",
    "title": "Users by Department"
}}
"""
    return gemini_generate_json(prompt)
