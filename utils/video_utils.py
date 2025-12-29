import os
import shutil
import logging
from moviepy.editor import (
    ImageClip, 
    TextClip, 
    CompositeVideoClip, 
    AudioFileClip, 
    concatenate_videoclips, 
    concatenate_audioclips
)
from moviepy.config import change_settings

# --- LOGGING SETUP ---
logger = logging.getLogger(__name__)

# --- IMAGEMAGICK CONFIGURATION ---
# This part automatically finds 'magick' on Linux (Streamlit) or Windows (Local)
def configure_imagemagick():
    # 1. Try to find 'magick' or 'convert' in the system PATH
    magick_path = shutil.which("magick") or shutil.which("convert")
    
    # 2. Fallback for common Windows installation path if not in PATH
    if not magick_path and os.name == 'nt':
        common_windows_path = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
        if os.path.exists(common_windows_path):
            magick_path = common_windows_path

    if magick_path:
        change_settings({"IMAGEMAGICK_BINARY": magick_path})
        logger.info(f"ImageMagick found at: {magick_path}")
    else:
        logger.error("ImageMagick binary not found. Video generation will fail.")

configure_imagemagick()

# --- SLIDE CREATION ---
def create_slide(image_path, title_text, content_text, audio_path):
    """
    Creates a single video slide with background image, text overlays, and audio.
    """
    # 1. Load Audio to get duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 2. Background Image
    # Resize to standard 1080p (1920x1080)
    img_clip = ImageClip(image_path).set_duration(duration).resize(height=1080)
    img_clip = img_clip.set_position('center')

    # 3. Title Text
    # Streamlit Cloud uses 'DejaVu-Sans' by default; Windows uses 'Arial'
    font = "DejaVu-Sans" if os.name != 'nt' else "Arial"
    
    title_clip = TextClip(
        title_text,
        fontsize=70,
        color='white',
        font=font,
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(1700, None)
    ).set_duration(duration).set_position(('center', 100))

    # 4. Content Text (Main Body)
    content_clip = TextClip(
        content_text,
        fontsize=45,
        color='yellow',
        font=font,
        stroke_color='black',
        stroke_width=1,
        method='caption',
        size=(1500, None)
    ).set_duration(duration).set_position(('center', 400))

    # 5. Overlay Graphics (Black gradient/shadow for readability)
    # Note: Simplified for this version to ensure it runs on Streamlit
    
    # 6. Compose the Video
    slide = CompositeVideoClip([img_clip, title_clip, content_clip], size=(1920, 1080))
    slide = slide.set_audio(audio_clip)

    # Optional: Add fades for smooth transitions
    return slide.crossfadein(0.5).crossfadeout(0.5)

# --- FINAL VIDEO COMPOSITION ---
def combine_slides_and_audio(video_clips, audio_paths, service_name=None):
    """
    Combines all individual slides into a single MP4 file.
    """
    # Concatenate all clips with a 'compose' method to handle different sizes
    final_video = concatenate_videoclips(video_clips, method="compose", padding=-0.5)

    # Create output directory
    output_dir = "output_videos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate Filename
    filename = "training_video.mp4"
    if service_name:
        safe_name = "".join([c for c in service_name if c.isalnum() or c in (' ', '_')]).rstrip()
        filename = f"Training_{safe_name.replace(' ', '_')}.mp4"
    
    output_path = os.path.join(output_dir, filename)

    # Write the video file
    # We use 'libx264' for high compatibility and 'aac' for audio
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

    return output_path
