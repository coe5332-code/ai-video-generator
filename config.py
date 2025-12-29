import os
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_URL = 'https://api.unsplash.com/search/photos'
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

VOICES = [
    'en-US-AriaNeural', 'en-US-GuyNeural', 'en-GB-SoniaNeural', 'en-AU-NatashaNeural',
    'en-IN-NeerjaNeural', 'en-CA-ClaraNeural', 'en-NZ-MollyNeural', 'en-ZA-LeahNeural'
]
