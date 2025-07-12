import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ffmpeg_availability():
    """
    Check if FFmpeg is available on the system.

    Returns:
        bool: True if FFmpeg is available, False otherwise.
    """
    try:
        # Use subprocess.run to check for ffmpeg command, hiding output
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        logging.info("FFmpeg is available on the system.")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        logging.error("FFmpeg is not installed or not found in system's PATH.")
        return False

# Check for FFmpeg availability on module import
FFMPEG_AVAILABLE = check_ffmpeg_availability()

def burn_subtitles_to_video(video_path: str, srt_path: str, output_dir: str,
                           output_filename: str = None, font_size: int = 24,
                           font_color: str = "white", position: str = "bottom") -> str:
    """
    Burns subtitles into a video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file.
        srt_path (str): Path to the SRT subtitle file.
        output_dir (str): Directory to save the output video.
        output_filename (str, optional): Name for the output file. Defaults to None.
        font_size (int, optional): Font size for the subtitles. Defaults to 24.
        font_color (str, optional): Font color for the subtitles. Defaults to "white".
        position (str, optional): Subtitle position ('bottom', 'top', 'center'). Defaults to "bottom".
    
    Returns:
        str: The path to the output video with burned-in subtitles.

    Raises:
        FileNotFoundError: If FFmpeg is not available, or video/SRT files are not found.
        Exception: For errors during the subtitle burning process.
    """
    if not FFMPEG_AVAILABLE:
        raise FileNotFoundError("FFmpeg is required but not available. Please install it.")

    if not Path(video_path).exists():
        raise FileNotFoundError(f"Input video file not found: {video_path}")
    if not Path(srt_path).exists():
        raise FileNotFoundError(f"Subtitle file not found: {srt_path}")
    
    # Generate an output filename if not provided
    if not output_filename:
        video_name = Path(video_path).stem
        output_filename = f"{video_name}_with_subtitles.mp4"
    
    output_path = Path(output_dir) / output_filename
    
    # --- FFmpeg Styling ---
    # Position mapping for the subtitles
    position_map = {"bottom": "Alignment=2", "top": "Alignment=8", "center": "Alignment=5"}
    alignment = position_map.get(position, "Alignment=2")
    
    # Color mapping for the subtitles (using FFmpeg's BGR format)
    color_map = {
        "white": "&HFFFFFF&", "yellow": "&H00FFFF&", "red": "&H0000FF&",
        "blue": "&HFF0000&", "green": "&H00FF00&", "black": "&H000000&"
    }
    color_code = color_map.get(font_color.lower(), "&HFFFFFF&")
    
    try:
        # Construct the FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"subtitles='{srt_path}':force_style='FontSize={font_size},PrimaryColour={color_code},{alignment}'",
            "-c:a", "copy",  # Copy audio stream without re-encoding
            "-y",            # Overwrite output file if it exists
            str(output_path)
        ]
        
        logging.info(f"Executing FFmpeg command: {' '.join(cmd)}")

        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600) # 1-hour timeout
        
        if result.returncode != 0:
            logging.error(f"FFmpeg failed with exit code {result.returncode}.")
            logging.error(f"FFmpeg stderr: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)
        
        if not output_path.exists():
            raise FileNotFoundError("Output video was not created by FFmpeg.")
        
        logging.info(f"Subtitles burned successfully to: {output_path}")
        return str(output_path)
        
    except subprocess.TimeoutExpired:
        logging.error("FFmpeg process timed out after 1 hour.")
        raise Exception("Video processing timed out.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg error: {e.stderr}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while burning subtitles: {e}")
        raise

def burn_subtitles_advanced(video_path: str, srt_path: str, output_dir: str, **kwargs) -> str:
    """
    Advanced subtitle burning with more styling options.
    
    Args:
        video_path (str): Path to the input video file.
        srt_path (str): Path to the SRT subtitle file.
        output_dir (str): Directory to save the output video.
        **kwargs: Advanced styling options like font_name, outline_color, etc.
    
    Returns:
        str: The path to the output video with styled subtitles.
    """
    if not FFMPEG_AVAILABLE:
        raise FileNotFoundError("FFmpeg is required for advanced subtitle burning.")

    if not Path(video_path).exists() or not Path(srt_path).exists():
        raise FileNotFoundError("Video or SRT file not found.")

    # --- Default and User-provided Styles ---
    styles = {
        "font_name": "Arial", "font_size": 24, "font_color": "white",
        "outline_color": "black", "outline_width": 2, "position": "bottom", "opacity": 1.0,
        **kwargs
    }
    
    output_filename = styles.get("output_filename") or f"{Path(video_path).stem}_styled.mp4"
    output_path = Path(output_dir) / output_filename
    
    # --- FFmpeg Styling ---
    position_map = {"bottom": "Alignment=2", "top": "Alignment=8", "center": "Alignment=5"}
    color_map = {
        "white": "&HFFFFFF&", "yellow": "&H00FFFF&", "red": "&H0000FF&",
        "blue": "&HFF0000&", "green": "&H00FF00&", "black": "&H000000&"
    }

    primary_color = color_map.get(styles['font_color'].lower(), "&HFFFFFF&")
    outline_color_code = color_map.get(styles['outline_color'].lower(), "&H000000&")
    alpha = f"&H{int((1.0 - styles['opacity']) * 255):02x}&"
    
    style_str = (
        f"FontName={styles['font_name']},FontSize={styles['font_size']},"
        f"PrimaryColour={primary_color},OutlineColour={outline_color_code},"
        f"Outline={styles['outline_width']},{position_map.get(styles['position'], '2')},"
        f"BackColour={alpha}"
    )
    
    try:
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vf", f"subtitles='{srt_path}':force_style='{style_str}'",
            "-c:a", "copy", "-y", str(output_path)
        ]
        
        logging.info("Executing advanced FFmpeg command.")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, stderr=result.stderr)

        return str(output_path)
        
    except Exception as e:
        logging.error(f"Advanced subtitle burning failed: {e}")
        raise

def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file using ffprobe.
    
    Args:
        video_path (str): Path to the video file.
        
    Returns:
        float: Duration of the video in seconds, or 0.0 if an error occurs.
    """
    if not FFMPEG_AVAILABLE:
        logging.warning("Cannot get video duration; FFprobe (part of FFmpeg) is not available.")
        return 0.0

    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip()) if result.returncode == 0 else 0.0
            
    except Exception as e:
        logging.error(f"Could not get video duration for {video_path}: {e}")
        return 0.0

def create_preview_with_subtitles(video_path: str, srt_path: str, output_dir: str,
                                  start_time: int = 0, duration: int = 30) -> str:
    """
    Creates a short video preview with burned-in subtitles.
    
    Args:
        video_path (str): Path to the input video.
        srt_path (str): Path to the SRT file.
        output_dir (str): Directory to save the preview.
        start_time (int, optional): Start time for the preview in seconds. Defaults to 0.
        duration (int, optional): Duration of the preview in seconds. Defaults to 30.
        
    Returns:
        str: The path to the created preview video, or None if failed.
    """
    if not FFMPEG_AVAILABLE:
        raise FileNotFoundError("FFmpeg is required to create video previews.")

    output_path = Path(output_dir) / f"preview_{Path(video_path).stem}_{start_time}s.mp4"
    
    try:
        cmd = [
            "ffmpeg", "-ss", str(start_time), "-i", video_path,
            "-t", str(duration), "-vf", f"subtitles='{srt_path}'",
            "-c:a", "copy", "-y", str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logging.info(f"Preview created successfully at {output_path}")
            return str(output_path)
        else:
            raise Exception(f"FFmpeg failed during preview creation: {result.stderr}")
            
    except Exception as e:
        logging.error(f"Failed to create video preview: {e}")
        raise
