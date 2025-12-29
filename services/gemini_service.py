import google.genai as genai
import json
import re
import os
import streamlit as st

# --- CONFIG ---
# Use Streamlit secrets for production, fallback to env vars for local
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in Streamlit Secrets or environment variables.")

client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.0-flash-lite" # Updated to current stable flash-lite version

# --- SAFE JSON EXTRACTOR ---
def extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())

# --- PROMPT ---
def build_prompt(raw_text: str) -> str:
    return f"""
You are creating PowerPoint slides for a government training video.
TASK: From the RAW TEXT below, create CLEAN, TRAINING-READY slides.
STRICT RULES (MANDATORY):
- Use ONLY information from the text.
- Generate ONLY the following slides if content exists: Service Overview, Application Process, Required Documents, Eligibility, Guidelines, Fees/Timeline, Tips, Troubleshooting.
- OUTPUT FORMAT (JSON ONLY):
{{
  "slides": [
    {{
      "slide_no": 1,
      "title": "Slide Title",
      "bullets": ["Point 1", "Point 2"],
      "image_keyword": "search term"
    }}
  ]
}}
RAW TEXT:
{raw_text}
"""

# --- GENERATE SLIDES ---
def generate_slides_from_raw(raw_text: str):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(raw_text),
    )
    data = extract_json(response.text)
    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Invalid slide structure from AI")
    for i, slide in enumerate(data["slides"], start=1):
        slide["slide_no"] = i
    return data
