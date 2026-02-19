
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Key being used: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, are you there?",
    )
    print("Success!")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
