import streamlit as st
import os
import tempfile
from pathlib import Path

from transcriber import transcribe_video
from translator import translate_srt
from subtitle_burner import burn_subtitles_to_video
from video_handler import get_video_info, extract_audio_from_video
from utils import create_temp_dir, cleanup_temp_files, format_time, get_available_languages

# --- Page Configuration ---
st.set_page_config(
    page_title="YoungAIVagent - AI Video Processor",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {}
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

def main():
    """Main function to run the Streamlit application."""
    st.title("🎬 YoungAIVagent - AI Video Processor")
    st.markdown("#### Transform your videos with AI-powered transcription, translation, and subtitle burning.")
    
    # --- Sidebar for Configuration ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key validation
        if not os.getenv("OPENAI_API_KEY"):
            st.error("⚠️ OpenAI API key not found. Please set the `OPENAI_API_KEY` environment variable.")
            st.stop()
        else:
            st.success("✅ OpenAI API key configured.")
        
        # Language selection
        st.subheader("🌐 Translation Languages")
        available_languages = list(get_available_languages().keys())
        target_languages = st.multiselect(
            "Select target languages:",
            options=available_languages,
            default=["Hebrew", "Spanish", "French"],
            help="Choose the languages to translate the subtitles into."
        )
        
        # Subtitle styling options
        st.subheader("🎨 Subtitle Styling")
        font_size = st.slider("Font Size", min_value=12, max_value=48, value=24, step=2)
        font_color = st.selectbox("Font Color", ["white", "yellow", "red", "blue", "green"], index=0)
        subtitle_position = st.selectbox("Position", ["bottom", "top", "center"], index=0)
        
        # Clean up button
        if st.button("🧹 Clean Temp Files"):
            cleanup_temp_files(st.session_state.temp_files)
            st.session_state.temp_files = []
            st.success("Temporary files have been cleaned up!")
    
    # --- Main Content Area ---
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "👁️ Preview", "📥 Download"])
    
    with tab1:
        st.header("1. Upload Your Video")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv'],
            help="Supported formats: MP4, AVI, MOV, MKV, WMV. Max size: 200MB."
        )
        
        if uploaded_file:
            display_video_info(uploaded_file)

            # Process button
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                if not target_languages:
                    st.warning("Please select at least one target language.")
                    return
                
                # Save uploaded file to a temporary directory
                temp_dir = create_temp_dir()
                video_path = Path(temp_dir) / uploaded_file.name
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.temp_files.append(temp_dir)
                
                process_video(video_path, uploaded_file.name, target_languages, font_size, font_color, subtitle_position, temp_dir)

    with tab2:
        st.header("🎬 Video Previews")
        display_previews()
    
    with tab3:
        st.header("📥 Download Your Files")
        display_downloads()

def display_video_info(uploaded_file):
    """Displays information about the uploaded video."""
    with st.expander("📊 Video Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Filename:** `{uploaded_file.name}`")
            st.write(f"**Size:** `{uploaded_file.size / (1024*1024):.2f} MB`")

        # To get more info, we need to save the file first
        temp_dir = create_temp_dir()
        video_path = Path(temp_dir) / uploaded_file.name
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            video_info = get_video_info(str(video_path))
            with col2:
                st.write(f"**Duration:** `{format_time(video_info.get('duration', 0))}`")
                st.write(f"**Resolution:** `{video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}`")
        except Exception as e:
            st.error(f"Could not read video metadata: {e}")
        finally:
            # Clean up the temporary file used for info extraction
            cleanup_temp_files([temp_dir])

def process_video(video_path, filename, target_languages, font_size, font_color, subtitle_position, temp_dir):
    """Orchestrates the video processing pipeline."""
    progress_container = st.container()
    
    with progress_container:
        st.info("🔄 Starting video processing pipeline...")
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- Step 1: Transcription ---
            status_text.text("1/4: Extracting audio...")
            audio_path = extract_audio_from_video(str(video_path), temp_dir)
            overall_progress.progress(10)
            
            status_text.text("2/4: Transcribing audio to generate subtitles...")
            srt_path = transcribe_video(audio_path, temp_dir)
            overall_progress.progress(30)
            
            if not Path(srt_path).exists():
                st.error("❌ Transcription failed: No SRT file was generated.")
                return
            st.success(f"✅ Transcription complete: `{Path(srt_path).name}`")
            
            # --- Step 2: Translation ---
            status_text.text("3/4: Translating subtitles...")
            translated_files = {}
            total_langs = len(target_languages)
            for i, lang in enumerate(target_languages):
                lang_progress = 30 + (40 * (i + 1) / total_langs)
                status_text.text(f"Translating to {lang} ({i+1}/{total_langs})...")
                try:
                    translated_srt = translate_srt(srt_path, lang, temp_dir)
                    translated_files[lang] = translated_srt
                    st.success(f"✅ Translation to {lang} complete.")
                except Exception as e:
                    st.error(f"❌ Translation to {lang} failed: {e}")
                overall_progress.progress(int(lang_progress))
            
            # --- Step 3: Subtitle Burning ---
            status_text.text("4/4: Burning subtitles into videos...")
            burned_videos = {}
            
            # Burn English (original) subtitles
            try:
                output_name = f"{Path(filename).stem}_english.mp4"
                english_video = burn_subtitles_to_video(str(video_path), srt_path, temp_dir, output_name, font_size, font_color, subtitle_position)
                burned_videos["English"] = english_video
                st.success("✅ English subtitles burned successfully.")
            except Exception as e:
                st.error(f"❌ Failed to burn English subtitles: {e}")
            
            # Burn translated subtitles
            total_burns = len(translated_files)
            for i, (lang, srt_file) in enumerate(translated_files.items()):
                burn_progress = 70 + (30 * (i + 1) / total_burns)
                try:
                    output_name = f"{Path(filename).stem}_{lang.lower()}.mp4"
                    burned_video = burn_subtitles_to_video(str(video_path), srt_file, temp_dir, output_name, font_size, font_color, subtitle_position)
                    burned_videos[lang] = burned_video
                    st.success(f"✅ {lang} subtitles burned successfully.")
                except Exception as e:
                    st.error(f"❌ Failed to burn {lang} subtitles: {e}")
                overall_progress.progress(int(burn_progress))
            
            overall_progress.progress(100)
            status_text.success("✅ All processing steps completed successfully!")
            
            # --- Store results in session state ---
            st.session_state.processing_status = {
                'original_video': str(video_path),
                'srt_files': {**{'English': srt_path}, **translated_files},
                'burned_videos': burned_videos,
                'temp_dir': temp_dir
            }
            st.info("🎉 Processing complete! You can now preview and download your files.")
            
        except Exception as e:
            st.error(f"❌ A critical error occurred during processing: {e}")
            status_text.text("❌ Processing failed.")

def display_previews():
    """Displays video previews in the 'Preview' tab."""
    if not st.session_state.processing_status:
        st.info("📹 Upload and process a video to see previews here.")
        return
    
    status = st.session_state.processing_status
    
    # Original video
    st.subheader("🎬 Original Video")
    if Path(status['original_video']).exists():
        st.video(status['original_video'])
    
    # Processed videos with subtitles
    if status.get('burned_videos'):
        st.subheader("📝 Videos with Burned-In Subtitles")
        for lang, video_path in status['burned_videos'].items():
            if Path(video_path).exists():
                with st.expander(f"**{lang} Version**", expanded=(lang=="English")):
                    st.video(video_path)
            else:
                st.error(f"❌ {lang} video file not found at path: {video_path}")

def display_downloads():
    """Displays download buttons for processed files."""
    if not st.session_state.processing_status:
        st.info("📁 Process a video to find downloadable files here.")
        return
    
    status = st.session_state.processing_status
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Subtitle Files (.srt)")
        for lang, srt_path in status.get('srt_files', {}).items():
            if Path(srt_path).exists():
                with open(srt_path, 'rb') as f:
                    st.download_button(
                        label=f"Download {lang} Subtitles",
                        data=f.read(),
                        file_name=f"subtitles_{lang.lower()}.srt",
                        mime="text/plain",
                        use_container_width=True
                    )
    
    with col2:
        st.subheader("🎬 Video Files (.mp4)")
        for lang, video_path in status.get('burned_videos', {}).items():
            if Path(video_path).exists():
                with open(video_path, 'rb') as f:
                    st.download_button(
                        label=f"Download {lang} Video",
                        data=f.read(),
                        file_name=Path(video_path).name,
                        mime="video/mp4",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
