"""
Gemini slide generator
RAW PDF text → CLEAN SLIDES (STRICT FORMAT)
"""

import google.genai as genai
import json
import re
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "PASTE_API_KEY_HERE"
GOOGLE_API_KEY = "AIzaSyD_jXVrYN4hQW3Vc_gpBuAlBonohC9peTw"  # REMOVE BEFORE SHARING CODE
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.5-flash-lite"

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

TASK:
From the RAW TEXT below, create CLEAN, TRAINING-READY slides.

STRICT RULES (MANDATORY):
- Use ONLY information from the text
- Do NOT invent or assume information
- Generate ONLY the following slides if content exists:
  1. Service Overview
  2. Application Process
  3. Required Documents
  4. Eligibility Criteria
  5. Important Guidelines
  6. Fees & Timeline
  7. Tips for DEO Operators
  8. Common Troubleshooting
  9. Online Service Access
  7. Thank You / Conclusion
- ONE slide per topic (DO NOT split)
- Skip a slide if no information exists 
- Compress long procedures into concise bullets

SLIDE RULES:
- Title: max 6 words (use topic name)
- Bullets: 4–6 bullets, max 12 words each
- Image keyword: exactly 2–3 words

OUTPUT FORMAT (JSON ONLY — EXACT):
{{
  "slides": [
    {{
      "slide_no": 1,
      "title": "",
      "bullets": [],
      "image_keyword": ""
    }}
  ]
}}

RAW TEXT:
{raw_text}
"""


# -------------------------------------------------
# GENERATE SLIDES
# -------------------------------------------------


def generate_slides_from_raw(raw_text: str):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(raw_text),
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


# -------------------------------------------------
# TEST
# -------------------------------------------------

if __name__ == "__main__":
    
    from utils.pdf_extractor import extract_raw_content
    PDF_PATH = r"C:\Users\techt\Downloads\ilovepdf_merged.pdf"
    RAW_CONTENT = extract_raw_content(PDF_PATH)
    slides = generate_slides_from_raw(RAW_CONTENT)
    print(json.dumps(slides, indent=2))
