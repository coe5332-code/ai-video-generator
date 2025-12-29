"""
Gemini slide generator
RAW PDF text → CLEAN SLIDES (STRICT FORMAT)
"""

import google.generativeai as genai
import json
import re
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.0-flash-exp"

# -------------------------------------------------
# SAFE JSON EXTRACTOR
# -------------------------------------------------
def extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())


# -------------------------------------------------
# PROMPT (STRICT OUTPUT CONTROL)
# -------------------------------------------------
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



# -------------------------------------------------
# GENERATE SLIDES
# -------------------------------------------------
def generate_slides_from_raw(raw_text: str):
    model = genai.GenerativeModel(MODEL_NAME)
    
    response = model.generate_content(
        build_prompt(raw_text),
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            top_p=0.8,
            top_k=40,
        )
    )

    data = extract_json(response.text)

    # -------------------------------------------------
    # HARD SAFETY CHECK
    # -------------------------------------------------
    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Invalid slide output from LLM")

    # Re-number slides safely
    for i, slide in enumerate(data["slides"], start=1):
        slide["slide_no"] = i

    return data
