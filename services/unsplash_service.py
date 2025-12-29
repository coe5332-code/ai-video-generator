import os
import requests
import hashlib
import streamlit as st
from urllib.parse import quote_plus

# --- CONFIG ---
UNSPLASH_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_ACCESS_KEY = st.secrets.get("UNSPLASH_ACCESS_KEY") or os.getenv("UNSPLASH_ACCESS_KEY")

# Ensure image directory exists (important for cloud persistence)
IMAGES_DIR = "images_cache"
FALLBACK_IMAGE = os.path.join("assets", "default_background.jpg")
os.makedirs(IMAGES_DIR, exist_ok=True)

def normalize_query(query: str) -> str:
    return query.lower().strip().replace("&", "and")

def cached_image_path(query: str) -> str:
    hash_key = hashlib.md5(query.encode("utf-8")).hexdigest()
    return os.path.join(IMAGES_DIR, f"{hash_key}.jpg")

def fetch_photo_from_unsplash(query: str):
    if not UNSPLASH_ACCESS_KEY:
        raise ValueError("Unsplash Access Key missing")
        
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {"query": quote_plus(query), "per_page": 1, "orientation": "landscape"}
    
    response = requests.get(UNSPLASH_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise ValueError("No images found")
    return results[0]

def fetch_and_save_photo(query: str) -> str:
    if not query or not query.strip():
        query = "government office training"
    query = normalize_query(query)
    image_path = cached_image_path(query)

    if os.path.exists(image_path):
        return image_path

    try:
        photo = fetch_photo_from_unsplash(query)
        image_url = photo["urls"]["regular"]
        image_data = requests.get(image_url, timeout=10).content
        with open(image_path, "wb") as f:
            f.write(image_data)
        return image_path
    except Exception as e:
        print(f"[Unsplash Error] {e}")
        return FALLBACK_IMAGE
