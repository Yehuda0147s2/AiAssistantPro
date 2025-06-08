import os
import subprocess
import tempfile
from pathlib import Path

def burn_subtitles_to_video(video_path, srt_path, output_dir, output_filename=None, 
                           font_size=24, font_color="white", position="bottom"):
    """
    Burn subtitles into video using FFmpeg
    
    Args:
        video_path (str): Path to input video file
        srt_path (str): Path to SRT subtitle file
        output_dir (str): Directory to save output video
        output_filename (str): Output filename (optional)
        font_size (int): Font size for subtitles
        font_color (str): Font color for subtitles
        position (str): Subtitle position ("bottom", "top", "center")
    
    Returns:
        str: Path to the output video with burned subtitles
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT file not found: {srt_path}")
    
    # Generate output filename if not provided
    if not output_filename:
        video_name = Path(video_path).stem
        output_filename = f"{video_name}_with_subtitles.mp4"
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Position mapping for FFmpeg
    position_map = {
        "bottom": "Alignment=2",  # Bottom center
        "top": "Alignment=8",     # Top center  
        "center": "Alignment=5"   # Middle center
    }
    
    alignment = position_map.get(position, "Alignment=2")
    
    # Color mapping for FFmpeg
    color_map = {
        "white": "&Hffffff&",
        "yellow": "&H00ffff&", 
        "red": "&H0000ff&",
        "blue": "&Hff0000&",
        "green": "&H00ff00&",
        "black": "&H000000&"
    }
    
    color_code = color_map.get(font_color.lower(), "&Hffffff&")
    
    try:
        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={srt_path}:force_style='FontSize={font_size},PrimaryColour={color_code},{alignment}'",
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",  # Overwrite output file if it exists
            output_path
        ]
        
        # Execute FFmpeg command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, 
                cmd, 
                output=result.stdout, 
                stderr=result.stderr
            )
        
        if not os.path.exists(output_path):
            raise FileNotFoundError("Output video was not created")
        
        return output_path
        
    except subprocess.TimeoutExpired:
        raise Exception("Video processing timed out after 1 hour")
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg failed with return code {e.returncode}"
        if e.stderr:
            error_msg += f"\nError output: {e.stderr}"
        raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"Failed to burn subtitles: {str(e)}")

def burn_subtitles_advanced(video_path, srt_path, output_dir, output_filename=None,
                           font_name="Arial", font_size=24, font_color="white", 
                           outline_color="black", outline_width=2, position="bottom",
                           opacity=1.0):
    """
    Advanced subtitle burning with more styling options
    
    Args:
        video_path (str): Path to input video file
        srt_path (str): Path to SRT subtitle file
        output_dir (str): Directory to save output video
        output_filename (str): Output filename (optional)
        font_name (str): Font family name
        font_size (int): Font size for subtitles
        font_color (str): Font color for subtitles
        outline_color (str): Outline color for subtitles
        outline_width (int): Outline width in pixels
        position (str): Subtitle position
        opacity (float): Subtitle opacity (0.0 to 1.0)
    
    Returns:
        str: Path to the output video with burned subtitles
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT file not found: {srt_path}")
    
    if not output_filename:
        video_name = Path(video_path).stem
        output_filename = f"{video_name}_styled_subtitles.mp4"
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Position mapping
    position_map = {
        "bottom": "Alignment=2",
        "top": "Alignment=8", 
        "center": "Alignment=5"
    }
    
    alignment = position_map.get(position, "Alignment=2")
    
    # Color mapping (BGR format for FFmpeg)
    color_map = {
        "white": "&Hffffff&",
        "yellow": "&H00ffff&",
        "red": "&H0000ff&", 
        "blue": "&Hff0000&",
        "green": "&H00ff00&",
        "black": "&H000000&"
    }
    
    primary_color = color_map.get(font_color.lower(), "&Hffffff&")
    outline_color_code = color_map.get(outline_color.lower(), "&H000000&")
    
    # Convert opacity to alpha (0-255)
    alpha = int((1.0 - opacity) * 255)
    alpha_hex = f"&H{alpha:02x}&"
    
    try:
        # Advanced style string
        style = (
            f"FontName={font_name},"
            f"FontSize={font_size},"
            f"PrimaryColour={primary_color},"
            f"OutlineColour={outline_color_code},"
            f"Outline={outline_width},"
            f"{alignment},"
            f"BackColour={alpha_hex}"
        )
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={srt_path}:force_style='{style}'",
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True,
            timeout=3600
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                output=result.stdout,
                stderr=result.stderr
            )
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Advanced subtitle burning failed: {str(e)}")

def check_ffmpeg_availability():
    """
    Check if FFmpeg is available on the system
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_video_duration(video_path):
    """
    Get video duration using FFprobe
    
    Args:
        video_path (str): Path to video file
        
    Returns:
        float: Duration in seconds
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            return 0.0
            
    except Exception:
        return 0.0

def create_preview_with_subtitles(video_path, srt_path, output_dir, start_time=0, duration=30):
    """
    Create a short preview video with subtitles
    
    Args:
        video_path (str): Path to input video
        srt_path (str): Path to SRT file
        output_dir (str): Output directory
        start_time (int): Start time in seconds
        duration (int): Preview duration in seconds
        
    Returns:
        str: Path to preview video
    """
    output_filename = f"preview_{start_time}s.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        cmd = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(duration),
            "-vf", f"subtitles={srt_path}",
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return output_path
        else:
            raise Exception(f"Preview creation failed: {result.stderr}")
            
    except Exception as e:
        raise Exception(f"Failed to create preview: {str(e)}")
