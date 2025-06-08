import streamlit as st
import os
import tempfile
import time
from pathlib import Path
import shutil

from transcriber import transcribe_video
from translator import translate_srt
from subtitle_burner import burn_subtitles_to_video
from video_handler import get_video_info, extract_audio_from_video
from utils import create_temp_dir, cleanup_temp_files, format_time

# Page configuration
st.set_page_config(
    page_title="YoungAIVagent - AI Video Processor",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {}
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

def main():
    st.title("🎬 YoungAIVagent - AI Video Processor")
    st.markdown("Transform your videos with AI-powered transcription, translation, and subtitle burning")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key validation
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            st.stop()
        else:
            st.success("✅ OpenAI API key configured")
        
        # Language selection
        st.subheader("Translation Languages")
        target_languages = st.multiselect(
            "Select target languages:",
            options=["Hebrew", "Spanish", "French", "German", "Italian", "Portuguese"],
            default=["Hebrew", "Spanish", "French"],
            help="Choose languages to translate subtitles into"
        )
        
        # Subtitle styling options
        st.subheader("Subtitle Styling")
        font_size = st.slider("Font Size", min_value=12, max_value=48, value=24)
        font_color = st.selectbox("Font Color", ["white", "yellow", "red", "blue", "green"], index=0)
        subtitle_position = st.selectbox("Position", ["bottom", "top", "center"], index=0)
        
        # Clean up button
        if st.button("🧹 Clean Temp Files"):
            cleanup_temp_files(st.session_state.temp_files)
            st.session_state.temp_files = []
            st.success("Temporary files cleaned up!")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "👁️ Preview", "📥 Download"])
    
    with tab1:
        st.header("Upload Video File")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv'],
            help="Supported formats: MP4, AVI, MOV, MKV, WMV (max 200MB)"
        )
        
        if uploaded_file is not None:
            # Display video info
            with st.expander("📊 Video Information", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Filename:** {uploaded_file.name}")
                    st.write(f"**Size:** {uploaded_file.size / (1024*1024):.2f} MB")
                
                # Save uploaded file temporarily
                temp_dir = create_temp_dir()
                video_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.temp_files.append(temp_dir)
                
                # Get video info
                try:
                    video_info = get_video_info(video_path)
                    with col2:
                        st.write(f"**Duration:** {format_time(video_info.get('duration', 0))}")
                        st.write(f"**Resolution:** {video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}")
                except Exception as e:
                    st.error(f"Error reading video info: {str(e)}")
                    return
            
            # Process button
            if st.button("🚀 Start Processing", type="primary"):
                if not target_languages:
                    st.error("Please select at least one target language")
                    return
                
                process_video(
                    video_path, 
                    uploaded_file.name,
                    target_languages,
                    font_size,
                    font_color,
                    subtitle_position,
                    temp_dir
                )
    
    with tab2:
        st.header("Video Preview")
        display_preview()
    
    with tab3:
        st.header("Download Processed Files")
        display_downloads()

def process_video(video_path, filename, target_languages, font_size, font_color, subtitle_position, temp_dir):
    """Process video through transcription, translation, and subtitle burning pipeline"""
    
    progress_container = st.container()
    
    with progress_container:
        st.info("🔄 Starting video processing pipeline...")
        
        # Overall progress
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract audio and transcribe
            status_text.text("Step 1/4: Extracting audio...")
            audio_path = extract_audio_from_video(video_path, temp_dir)
            overall_progress.progress(0.1)
            
            status_text.text("Step 2/4: Transcribing audio...")
            srt_path = transcribe_video(audio_path, temp_dir)
            overall_progress.progress(0.3)
            
            if not os.path.exists(srt_path):
                st.error("❌ Transcription failed - no SRT file generated")
                return
            
            st.success(f"✅ Transcription completed: {os.path.basename(srt_path)}")
            
            # Step 2: Translation
            status_text.text("Step 3/4: Translating subtitles...")
            translated_files = {}
            
            for i, lang in enumerate(target_languages):
                lang_progress = 0.3 + (0.4 * (i + 1) / len(target_languages))
                status_text.text(f"Translating to {lang}...")
                
                try:
                    translated_srt = translate_srt(srt_path, lang, temp_dir)
                    translated_files[lang] = translated_srt
                    st.success(f"✅ Translation to {lang} completed")
                except Exception as e:
                    st.error(f"❌ Translation to {lang} failed: {str(e)}")
                    continue
                
                overall_progress.progress(lang_progress)
            
            # Step 3: Burn subtitles
            status_text.text("Step 4/4: Burning subtitles to video...")
            burned_videos = {}
            
            # Original with English subtitles
            try:
                english_video = burn_subtitles_to_video(
                    video_path, srt_path, temp_dir, 
                    f"{Path(filename).stem}_english.mp4",
                    font_size, font_color, subtitle_position
                )
                burned_videos["English"] = english_video
                st.success("✅ English subtitles burned to video")
            except Exception as e:
                st.error(f"❌ Failed to burn English subtitles: {str(e)}")
            
            # Translated versions
            for i, (lang, srt_file) in enumerate(translated_files.items()):
                try:
                    output_name = f"{Path(filename).stem}_{lang.lower()}.mp4"
                    burned_video = burn_subtitles_to_video(
                        video_path, srt_file, temp_dir, output_name,
                        font_size, font_color, subtitle_position
                    )
                    burned_videos[lang] = burned_video
                    st.success(f"✅ {lang} subtitles burned to video")
                except Exception as e:
                    st.error(f"❌ Failed to burn {lang} subtitles: {str(e)}")
                
                final_progress = 0.7 + (0.3 * (i + 1) / len(translated_files))
                overall_progress.progress(final_progress)
            
            overall_progress.progress(1.0)
            status_text.text("✅ Processing completed successfully!")
            
            # Store results in session state
            st.session_state.processing_status = {
                'original_video': video_path,
                'srt_files': {**{'English': srt_path}, **translated_files},
                'burned_videos': burned_videos,
                'temp_dir': temp_dir
            }
            
            st.success("🎉 Video processing completed! Check the Preview and Download tabs.")
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            status_text.text("❌ Processing failed")

def display_preview():
    """Display video previews"""
    if 'processing_status' not in st.session_state or not st.session_state.processing_status:
        st.info("📹 Upload and process a video first to see previews")
        return
    
    status = st.session_state.processing_status
    
    # Original video
    st.subheader("🎬 Original Video")
    if os.path.exists(status['original_video']):
        st.video(status['original_video'])
    
    # Processed videos with subtitles
    if status.get('burned_videos'):
        st.subheader("📝 Videos with Subtitles")
        
        for lang, video_path in status['burned_videos'].items():
            if os.path.exists(video_path):
                st.write(f"**{lang} Version:**")
                st.video(video_path)
            else:
                st.error(f"❌ {lang} video file not found")

def display_downloads():
    """Display download options for processed files"""
    if 'processing_status' not in st.session_state or not st.session_state.processing_status:
        st.info("📁 Process a video first to download files")
        return
    
    status = st.session_state.processing_status
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Subtitle Files (.srt)")
        for lang, srt_path in status.get('srt_files', {}).items():
            if os.path.exists(srt_path):
                with open(srt_path, 'rb') as f:
                    st.download_button(
                        label=f"📄 Download {lang} Subtitles",
                        data=f.read(),
                        file_name=f"subtitles_{lang.lower()}.srt",
                        mime="text/plain"
                    )
    
    with col2:
        st.subheader("🎬 Video Files (.mp4)")
        for lang, video_path in status.get('burned_videos', {}).items():
            if os.path.exists(video_path):
                with open(video_path, 'rb') as f:
                    st.download_button(
                        label=f"🎬 Download {lang} Video",
                        data=f.read(),
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )

if __name__ == "__main__":
    main()
