import re
import json
from openai import OpenAI
import google.generativeai as genai
from settings import REQUIRED_KEYS


def parse_bug_json(raw: str):
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    js = m.group(0) if m else raw
    bug = json.loads(js)
    missing = REQUIRED_KEYS.difference(bug)
    if missing:
        raise ValueError(f"Missing keys: {', '.join(missing)}")
    return bug


def call_openai_model(model, prompt, api_key):
    client = OpenAI(api_key=api_key)
    res = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You format bug reports as JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )
    return res.choices[0].message.content


def call_gemini_model(model, prompt, api_key):
    genai.configure(api_key=api_key)
    gemodel = genai.GenerativeModel(model)
    response = gemodel.generate_content(prompt)
    if hasattr(response, "text") and response.text:
        return response.text
    elif hasattr(response, "candidates") and response.candidates:
        return response.candidates[0].content.parts[0].text
    else:
        raise RuntimeError("Gemini: No response returned")
