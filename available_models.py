import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
default_gemini = os.getenv("GEMINI_API_KEY", "")

genai.configure(api_key=default_gemini)

for m in genai.list_models():
    print(m.name, "| Supported methods:", m.supported_generation_methods)
