import streamlit as st
import asyncio
import logging
import os
import tempfile

from utils.service_utils import create_service_sections, validate_service_content
from utils.audio_utils import text_to_speech
from utils.video_utils import create_slide, combine_slides_and_audio
from services.unsplash_service import fetch_and_save_photo
from services.gemini_service import generate_slides_from_raw
from utils.avatar_utils import add_avatar_to_slide
from utils.pdf_extractor import extract_raw_content
from utils.pdf_utils import generate_service_pdf
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"}
)

logging.basicConfig(level=logging.INFO)

VOICES = {
    "en-IN-NeerjaNeural": "Neerja (Female, Indian English)",
    "en-IN-PrabhatNeural": "Prabhat (Male, Indian English)",
}


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    st.set_page_config(
        page_title="BSK Training Video Generator",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load CSS
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("### 🎥 BSK Training Generator")
        st.markdown("**Professional Training Videos**")
        st.markdown("*Bangla Sahayta Kendra*")
        st.markdown("---")

        page = st.selectbox(
            "Select Page:",
            ["🎬 Create New Video", "📂 View Existing Videos"],
            key="page_selector",
        )

        st.markdown("---")

        voice_keys = list(VOICES.keys())
        voice_labels = list(VOICES.values())
        voice_index = st.selectbox(
            "Select Narrator Voice:",
            range(len(voice_keys)),
            format_func=lambda i: voice_labels[i],
        )
        selected_voice = voice_keys[voice_index]

        st.markdown("---")
        st.markdown("### 📄 Optional Service PDF")
        uploaded_pdf = st.file_uploader(
            "Upload PDF (Overrides form)",
            type=["pdf"],
            help="If provided, form content will be ignored",
        )

        st.markdown("### 🧑‍🏫 AI Avatar")
        st.caption("Avatar will appear inside the generated training video.")

    # ---------------- ROUTING ----------------
    if page == "🎬 Create New Video":
        show_create_video_page(selected_voice, uploaded_pdf)
    else:
        show_existing_videos_page()


# -------------------------------------------------
# CREATE VIDEO PAGE
# -------------------------------------------------
def show_create_video_page(selected_voice, uploaded_pdf):
    st.title("🎥 BSK Training Video Generator")
    st.markdown("**Create training videos for BSK data entry operators**")
    st.markdown("---")

    # ---------------- FORM UI (UNCHANGED) ----------------
    with st.form("service_form"):
        st.subheader("📋 Service Training Information")

        col1, col2 = st.columns(2)

        with col1:
            service_name = st.text_input("Service Name *")
            service_description = st.text_area("Service Description *", height=100)

        with col2:
            how_to_apply = st.text_area(
                "Step-by-Step Application Process *", height=100
            )
            eligibility_criteria = st.text_area("Eligibility Criteria *", height=100)
            required_docs = st.text_area("Required Documents *", height=100)

        st.subheader("🎯 Training Specific Information")
        col3, col4 = st.columns(2)

        with col3:
            operator_tips = st.text_area("Operator Tips", height=100)
            service_link = st.text_input("Official Service Link")

        with col4:
            troubleshooting = st.text_area("Common Issues", height=100)
            fees_and_timeline = st.text_input("Fees & Processing Time")

        submitted = st.form_submit_button("🚀 Generate Training Video")

    # ---------------- GENERATION LOGIC ----------------
    if submitted:
        try:
            progress = st.progress(0)
            status = st.empty()

            video_clips = []
            audio_paths = []

            # ==================================================
            # CASE 1: PDF EXISTS → IGNORE FORM
            # ==================================================
            if uploaded_pdf:
                status.text("📄 Extracting content from PDF (form ignored)...")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_pdf.read())
                    pdf_path = tmp.name

                pages = extract_raw_content(pdf_path)
                raw_text = "\n".join(line for page in pages for line in page["lines"])

            # ==================================================
            # CASE 2: FORM → RAW TEXT
            # ==================================================
            else:
                service_content = {
                    "service_name": service_name,
                    "service_description": service_description,
                    "how_to_apply": how_to_apply,
                    "eligibility_criteria": eligibility_criteria,
                    "required_docs": required_docs,
                    "operator_tips": operator_tips,
                    "troubleshooting": troubleshooting,
                    "service_link": service_link,
                    "fees_and_timeline": fees_and_timeline,
                }

                valid, msg = validate_service_content(service_content)
                if not valid:
                    st.error(msg)
                    return

                # 1️⃣ Generate & SAVE PDF
                status.text("📄 Generating training PDF from form...")
                pdf_path = generate_service_pdf(service_content)

                # Optional: show download button
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Download Training PDF",
                        data=f.read(),
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                    )

                # 2️⃣ Extract text from the saved PDF
                pages = extract_raw_content(pdf_path)
                raw_text = "\n".join(line for page in pages for line in page["lines"])

            # ==================================================
            # GEMINI → SLIDES (NEW API)
            # ==================================================
            status.text("🧠 Structuring training slides using AI...")
            slides_response = generate_slides_from_raw(raw_text)
            slides = slides_response["slides"]

            # ==================================================
            # VIDEO PIPELINE
            # ==================================================
            for i, slide in enumerate(slides):
                status.text(f"🎬 Creating slide {i + 1}/{len(slides)}")

                narration = " ".join(slide["bullets"])
                audio = asyncio.run(text_to_speech(narration, voice=selected_voice))
                audio_paths.append(audio)

                try:
                    image = fetch_and_save_photo(slide["image_keyword"])
                except Exception:
                    image = os.path.join("assets", "default_background.jpg")

                clip = create_slide(slide["title"], slide["bullets"], image, audio)
                clip = add_avatar_to_slide(clip, audio_duration=clip.duration)
                video_clips.append(clip)
                progress.progress(int((i + 1) / len(slides) * 80))

            status.text("🎞️ Rendering final video...")
            final_path = combine_slides_and_audio(
                video_clips, audio_paths, service_name=service_name or "BSK_Service"
            )

            progress.progress(100)
            st.session_state["video_path"] = final_path
            st.session_state["audio_paths"] = audio_paths

            status.empty()
            progress.empty()

            st.success("✅ Training video generated successfully!")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error generating video: {e}")

    # ---------------- DISPLAY RESULT ----------------
    if "video_path" in st.session_state:
        st.markdown("---")
        st.subheader("🎬 Generated Training Video")

        with open(st.session_state["video_path"], "rb") as f:
            st.video(f.read())

        st.download_button(
            "📥 Download Video",
            data=open(st.session_state["video_path"], "rb").read(),
            file_name=os.path.basename(st.session_state["video_path"]),
            mime="video/mp4",
        )

        if st.button("🔄 Generate New"):
            st.session_state.clear()
            st.rerun()


# -------------------------------------------------
# EXISTING VIDEOS PAGE (UNCHANGED)
# -------------------------------------------------
def show_existing_videos_page():
    st.title("📂 Existing Training Videos")
    st.markdown("---")

    output_dir = "output_videos"
    if not os.path.exists(output_dir):
        st.info("No videos found.")
        return

    videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
    if not videos:
        st.info("No videos available.")
        return

    selected = st.selectbox("Select a video:", videos)
    path = os.path.join(output_dir, selected)

    with open(path, "rb") as f:
        st.video(f.read())


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    main()
