import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ffmpeg_tools() -> Dict[str, bool]:
    """
    Checks for the availability of FFmpeg and FFprobe.

    Returns:
        Dict[str, bool]: A dictionary indicating the availability of each tool.
    """
    status = {'ffmpeg': False, 'ffprobe': False}
    for tool in status:
        try:
            subprocess.run([tool, "-version"], capture_output=True, text=True, check=True)
            status[tool] = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            logging.warning(f"{tool.capitalize()} is not installed or not in PATH.")
    return status

FFMPEG_TOOLS_AVAILABLE = check_ffmpeg_tools()

# --- Core Video Operations ---

def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Retrieves detailed video information using ffprobe.
    
    Args:
        video_path (str): The path to the video file.
        
    Returns:
        Dict[str, Any]: A dictionary with video metadata.

    Raises:
        FileNotFoundError: If the video file is not found or ffprobe is unavailable.
        Exception: For errors during ffprobe execution or JSON parsing.
    """
    if not FFMPEG_TOOLS_AVAILABLE['ffprobe']:
        raise FileNotFoundError("FFprobe is required to get video info but is not available.")
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        probe_data = json.loads(result.stdout)
        
        # Extract primary video and audio streams
        video_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        
        format_info = probe_data.get('format', {})
        
        # Safely evaluate frame rate
        fps_str = video_stream.get('r_frame_rate', '0/1') if video_stream else '0/1'
        try:
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den else 0
        except (ValueError, ZeroDivisionError):
            fps = 0

        info = {
            'filename': Path(video_path).name,
            'duration': float(format_info.get('duration', 0)),
            'size_bytes': int(format_info.get('size', 0)),
            'format_name': format_info.get('format_name'),
            'bit_rate': int(format_info.get('bit_rate', 0)),
            'width': video_stream.get('width', 0) if video_stream else 0,
            'height': video_stream.get('height', 0) if video_stream else 0,
            'video_codec': video_stream.get('codec_name') if video_stream else None,
            'fps': fps,
            'audio_codec': audio_stream.get('codec_name') if audio_stream else None,
            'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
            'audio_channels': audio_stream.get('channels', 0) if audio_stream else 0
        }
        return info
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"ffprobe failed: {e.stderr}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse ffprobe output.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while getting video info: {e}")

def extract_audio_from_video(video_path: str, output_dir: str, audio_format: str = "wav") -> str:
    """
    Extracts the audio track from a video file and saves it in the desired format.
    
    Args:
        video_path (str): The path to the input video file.
        output_dir (str): The directory to save the extracted audio.
        audio_format (str, optional): The output audio format ('wav' or 'mp3'). Defaults to "wav".
        
    Returns:
        str: The path to the extracted audio file.
    """
    if not FFMPEG_TOOLS_AVAILABLE['ffmpeg']:
        raise FileNotFoundError("FFmpeg is required to extract audio but is not available.")

    video_p = Path(video_path)
    output_audio_path = Path(output_dir) / f"{video_p.stem}.{audio_format}"

    cmd = [
        "ffmpeg", "-i", str(video_p),
        "-vn",  # No video
        "-acodec", "pcm_s16le" if audio_format == "wav" else "libmp3lame",
        "-ac", "1",      # Mono audio
        "-ar", "16000",  # 16kHz sample rate
        "-y", str(output_audio_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=True)
        logging.info(f"Audio extracted successfully to: {output_audio_path}")
        return str(output_audio_path)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Audio extraction failed: {e.stderr}")

# --- Utility Video Functions ---

def validate_video_file(video_path: str) -> Dict[str, Any]:
    """
    Performs a basic validation of a video file's properties.
    
    Args:
        video_path (str): The path to the video file.
        
    Returns:
        Dict[str, Any]: A dictionary with validation status, errors, and warnings.
    """
    result = {'is_valid': False, 'errors': [], 'warnings': []}
    
    if not Path(video_path).exists():
        result['errors'].append("Video file does not exist.")
        return result
    
    try:
        info = get_video_info(video_path)
        if not info.get('duration') or info['duration'] <= 0:
            result['errors'].append("Video has zero or invalid duration.")
        if not info.get('width') or info['width'] <= 0:
            result['errors'].append("Video has invalid resolution.")
        if not info.get('audio_codec'):
            result['errors'].append("No audio track found, which is required for transcription.")

        if not result['errors']:
            result['is_valid'] = True

    except Exception as e:
        result['errors'].append(f"Cannot read video file metadata: {e}")
    
    return result

def create_video_thumbnail(video_path: str, output_dir: str, timestamp: str = "00:00:10") -> Optional[str]:
    """
    Creates a thumbnail image from a video at a specific timestamp.
    
    Args:
        video_path (str): The path to the video file.
        output_dir (str): The directory to save the thumbnail.
        timestamp (str, optional): The timestamp for the thumbnail (HH:MM:SS). Defaults to "00:00:10".
        
    Returns:
        Optional[str]: The path to the thumbnail, or None if creation fails.
    """
    if not FFMPEG_TOOLS_AVAILABLE['ffmpeg']:
        logging.error("FFmpeg is required to create thumbnails.")
        return None

    thumb_path = Path(output_dir) / f"{Path(video_path).stem}_thumbnail.jpg"
    cmd = ["ffmpeg", "-i", video_path, "-ss", timestamp, "-vframes", "1", "-q:v", "2", "-y", str(thumb_path)]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        return str(thumb_path)
    except subprocess.CalledProcessError as e:
        logging.error(f"Thumbnail creation failed: {e.stderr}")
        return None

def compress_video(video_path: str, output_dir: str, quality: str = "medium") -> Optional[str]:
    """
    Compresses a video to reduce its file size.
    
    Args:
        video_path (str): The path to the input video.
        output_dir (str): The directory to save the compressed video.
        quality (str, optional): Compression quality ('low', 'medium', 'high'). Defaults to "medium".
        
    Returns:
        Optional[str]: The path to the compressed video, or None if compression fails.
    """
    if not FFMPEG_TOOLS_AVAILABLE['ffmpeg']:
        logging.error("FFmpeg is required for video compression.")
        return None

    settings = {
        "low": {"crf": "28", "preset": "fast"},
        "medium": {"crf": "23", "preset": "medium"},
        "high": {"crf": "18", "preset": "slow"}
    }.get(quality, {"crf": "23", "preset": "medium"})
    
    compressed_path = Path(output_dir) / f"{Path(video_path).stem}_compressed.mp4"
    cmd = [
        "ffmpeg", "-i", video_path,
        "-c:v", "libx264", "-crf", settings["crf"], "-preset", settings["preset"],
        "-c:a", "aac", "-b:a", "128k",
        "-y", str(compressed_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=1800, check=True)
        return str(compressed_path)
    except subprocess.CalledProcessError as e:
        logging.error(f"Video compression failed: {e.stderr}")
        return None
