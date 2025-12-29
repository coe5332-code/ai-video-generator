import streamlit as st
import asyncio
import logging
import os
import tempfile
import shutil

from moviepy.config import change_settings
from utils.service_utils import create_service_sections, validate_service_content
from utils.audio_utils import text_to_speech
from utils.video_utils import create_slide, combine_slides_and_audio
from services.unsplash_service import fetch_and_save_photo
from services.gemini_service import generate_slides_from_raw
from utils.avatar_utils import add_avatar_to_slide
from utils.pdf_extractor import extract_raw_content
from utils.pdf_utils import generate_service_pdf

# --- DYNAMIC BINARY CONFIG ---
def init_binaries():
    # Detect ImageMagick location (Linux vs Windows)
    magick_path = shutil.which("magick") or shutil.which("convert")
    if magick_path:
        change_settings({"IMAGEMAGICK_BINARY": magick_path})
    elif os.name == 'nt': # Fallback for local Windows testing only
        win_path = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
        if os.path.exists(win_path):
            change_settings({"IMAGEMAGICK_BINARY": win_path})

init_binaries()
logging.basicConfig(level=logging.INFO)

VOICES = {
    "en-IN-NeerjaNeural": "Neerja (Female, Indian English)",
    "en-IN-PrabhatNeural": "Prabhat (Male, Indian English)",
}

def main():
    st.set_page_config(page_title="BSK Training Video Generator", page_icon="🎥", layout="wide")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        page = st.selectbox("Select Page:", ["🎬 Create New Video", "📂 View Existing Videos"])
        selected_voice = st.selectbox("Select Narrator:", list(VOICES.keys()), format_func=lambda x: VOICES[x])
        uploaded_pdf = st.file_uploader("Upload PDF (Optional)", type=["pdf"])

    if page == "🎬 Create New Video":
        show_create_page(selected_voice, uploaded_pdf)
    else:
        show_existing_videos_page()

def show_create_page(selected_voice, uploaded_pdf):
    st.title("🎥 BSK Training Video Generator")
    
    with st.form("service_form"):
        col1, col2 = st.columns(2)
        with col1:
            service_name = st.text_input("Service Name *")
            service_description = st.text_area("Description")
        with col2:
            how_to_apply = st.text_area("Application Process")
            eligibility = st.text_area("Eligibility")
        
        submitted = st.form_submit_button("🚀 Generate Video")

    if submitted:
        try:
            status = st.empty()
            progress = st.progress(0)
            
            # Step 1: Get Content
            if uploaded_pdf:
                status.text("📄 Reading PDF...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_pdf.read())
                    pdf_path = tmp.name
                pages = extract_raw_content(pdf_path)
                raw_text = "\n".join(line for page in pages for line in page["lines"])
            else:
                status.text("📄 Preparing form data...")
                raw_text = f"{service_name}\n{service_description}\n{how_to_apply}\n{eligibility}"

            # Step 2: AI Slide Generation
            status.text("🧠 AI Structuring Content...")
            slides_data = generate_slides_from_raw(raw_text)
            slides = slides_data["slides"]

            # Step 3: Creation Loop
            video_clips = []
            audio_paths = []

            for i, slide in enumerate(slides):
                status.text(f"🎬 Processing Slide {i+1}/{len(slides)}")
                narration = " ".join(slide["bullets"])
                
                # TTS & Image
                audio = asyncio.run(text_to_speech(narration, voice=selected_voice))
                audio_paths.append(audio)
                image = fetch_and_save_photo(slide["image_keyword"])
                
                # Video Clip Creation
                clip = create_slide(image, slide["title"], narration, audio)
                clip = add_avatar_to_slide(clip, clip.duration)
                video_clips.append(clip)
                progress.progress((i + 1) / len(slides))

            # Step 4: Final Export
            status.text("🎞️ Rendering MP4...")
            final_video = combine_slides_and_audio(video_clips, audio_paths, service_name)
            
            st.success("Video Ready!")
            st.video(final_video)
            
        except Exception as e:
            st.error(f"Generation Error: {e}")

def show_existing_videos_page():
    st.title("📂 Library")
    output_dir = "output_videos"
    if os.path.exists(output_dir):
        videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
        if videos:
            selected = st.selectbox("Select Video", videos)
            st.video(os.path.join(output_dir, selected))
        else:
            st.info("No videos generated yet.")

if __name__ == "__main__":
    main()
