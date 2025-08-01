import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use the same API key name as config.py
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

def gemini_generate_json(prompt):
    """Generate JSON response from Gemini"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response if it has code blocks
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response_text}")
        return {}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {}
