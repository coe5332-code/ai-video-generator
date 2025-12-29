import google.genai as genai
from google.api_core import exceptions
import json
import re
import os
import time
import streamlit as st

# --- CONFIG ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Missing GOOGLE_API_KEY. Please add it to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

# SWITCHED TO 1.5 FLASH: More stable free tier quota than 2.0-lite
MODEL_NAME = "gemini-1.5-flash" 

# --- SAFE JSON EXTRACTOR ---
def extract_json(text: str):
    # Cleans Markdown code blocks if Gemini wraps the JSON in ```json ... ```
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())

# --- PROMPT ---
def build_prompt(raw_text: str) -> str:
    return f"""
You are creating PowerPoint slides for a government training video.
TASK: From the RAW TEXT below, create CLEAN, TRAINING-READY slides.

STRICT RULES:
- Use ONLY information from the text.
- Create 5-8 slides covering: Overview, Process, Eligibility, Documents, Fees, and Tips.
- OUTPUT FORMAT (JSON ONLY):
{{
  "slides": [
    {{
      "slide_no": 1,
      "title": "Slide Title",
      "bullets": ["Bullet 1", "Bullet 2"],
      "image_keyword": "high quality photo of [subject]"
    }}
  ]
}}

RAW TEXT:
{raw_text[:10000]} 
"""

# --- GENERATE SLIDES WITH RETRY LOGIC ---
def generate_slides_from_raw(raw_text: str, retries=3, delay=5):
    """
    Attempts to generate slides. If a 429 error occurs, it waits and retries.
    """
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=build_prompt(raw_text),
            )
            
            data = extract_json(response.text)
            
            # Validation
            if "slides" not in data or not isinstance(data["slides"], list):
                raise ValueError("Invalid slide structure")
                
            for i, slide in enumerate(data["slides"], start=1):
                slide["slide_no"] = i
            
            return data

        except Exception as e:
            # Check if error is Rate Limit (429)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < retries - 1:
                    st.warning(f"Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                    time.sleep(delay)
                    continue
                else:
                    st.error("Gemini API Quota exhausted. Please wait 1 minute and try again.")
                    raise e
            else:
                # If it's a different error, don't retry
                st.error(f"AI Generation Error: {e}")
                raise e
