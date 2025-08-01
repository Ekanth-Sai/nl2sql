import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def gemini_generate_json(prompt):
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.strip())
    except Exception:
        print("Gemini response not valid JSON.")
        return {}
