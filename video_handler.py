import os
import subprocess
import tempfile
from pathlib import Path
import json

def get_video_info(video_path):
    """
    Get detailed video information using ffprobe
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Video information including duration, resolution, codec, etc.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        # Use ffprobe to get video information
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        
        probe_data = json.loads(result.stdout)
        
        # Extract video stream information
        video_stream = None
        audio_stream = None
        
        for stream in probe_data.get('streams', []):
            if stream.get('codec_type') == 'video' and video_stream is None:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and audio_stream is None:
                audio_stream = stream
        
        # Extract format information
        format_info = probe_data.get('format', {})
        
        video_info = {
            'filename': os.path.basename(video_path),
            'duration': float(format_info.get('duration', 0)),
            'size_bytes': int(format_info.get('size', 0)),
            'format_name': format_info.get('format_name', 'unknown'),
            'bit_rate': int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else 0
        }
        
        # Add video stream info if available
        if video_stream:
            video_info.update({
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'video_codec': video_stream.get('codec_name', 'unknown'),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream.get('r_frame_rate') else 0,
                'pixel_format': video_stream.get('pix_fmt', 'unknown')
            })
        
        # Add audio stream info if available
        if audio_stream:
            video_info.update({
                'audio_codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream.get('sample_rate') else 0,
                'audio_channels': audio_stream.get('channels', 0)
            })
        
        return video_info
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get video info: {e.stderr}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse video info: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting video info: {str(e)}")

def extract_audio_from_video(video_path, output_dir, audio_format="wav"):
    """
    Extract audio from video file
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory to save the extracted audio
        audio_format (str): Output audio format (wav, mp3, m4a)
        
    Returns:
        str: Path to the extracted audio file
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Create output filename
    video_name = Path(video_path).stem
    audio_filename = f"{video_name}.{audio_format}"
    audio_path = os.path.join(output_dir, audio_filename)
    
    try:
        # Build ffmpeg command for audio extraction
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le" if audio_format == "wav" else "libmp3lame",
            "-ac", "1",  # Mono audio (better for transcription)
            "-ar", "16000",  # 16kHz sample rate (optimal for Whisper)
            "-y",  # Overwrite output file
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError("Audio extraction failed - output file not created")
        
        return audio_path
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Audio extraction failed: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")

def validate_video_file(video_path):
    """
    Validate video file format and basic properties
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Validation results with status and messages
    """
    validation_result = {
        'valid': False,
        'errors': [],
        'warnings': []
    }
    
    # Check if file exists
    if not os.path.exists(video_path):
        validation_result['errors'].append("Video file does not exist")
        return validation_result
    
    # Check file size (should be reasonable)
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if file_size_mb > 500:  # 500MB limit
        validation_result['warnings'].append(f"Large file size: {file_size_mb:.1f}MB")
    elif file_size_mb < 0.1:  # Less than 100KB
        validation_result['errors'].append("File too small to be a valid video")
        return validation_result
    
    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v']
    file_ext = Path(video_path).suffix.lower()
    if file_ext not in valid_extensions:
        validation_result['warnings'].append(f"Uncommon video format: {file_ext}")
    
    try:
        # Try to get video info using ffprobe
        video_info = get_video_info(video_path)
        
        # Check duration
        duration = video_info.get('duration', 0)
        if duration <= 0:
            validation_result['errors'].append("Invalid or zero duration")
        elif duration > 3600:  # More than 1 hour
            validation_result['warnings'].append(f"Long video: {duration/60:.1f} minutes")
        
        # Check resolution
        width = video_info.get('width', 0)
        height = video_info.get('height', 0)
        if width <= 0 or height <= 0:
            validation_result['errors'].append("Invalid video resolution")
        
        # Check if video has audio (required for transcription)
        if 'audio_codec' not in video_info or video_info['audio_codec'] == 'unknown':
            validation_result['errors'].append("No audio track found - required for transcription")
        
        if not validation_result['errors']:
            validation_result['valid'] = True
        
    except Exception as e:
        validation_result['errors'].append(f"Cannot read video file: {str(e)}")
    
    return validation_result

def create_video_thumbnail(video_path, output_dir, timestamp="00:00:10"):
    """
    Create a thumbnail image from video at specified timestamp
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the thumbnail
        timestamp (str): Timestamp in format HH:MM:SS
        
    Returns:
        str: Path to the created thumbnail file
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video_name = Path(video_path).stem
    thumbnail_path = os.path.join(output_dir, f"{video_name}_thumbnail.jpg")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", timestamp,
            "-vframes", "1",
            "-q:v", "2",  # High quality
            "-y",
            thumbnail_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        
        return thumbnail_path
        
    except Exception as e:
        raise Exception(f"Thumbnail creation failed: {str(e)}")

def compress_video(video_path, output_dir, quality="medium"):
    """
    Compress video to reduce file size
    
    Args:
        video_path (str): Path to input video
        output_dir (str): Directory to save compressed video
        quality (str): Compression quality ("low", "medium", "high")
        
    Returns:
        str: Path to compressed video
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video_name = Path(video_path).stem
    compressed_path = os.path.join(output_dir, f"{video_name}_compressed.mp4")
    
    # Quality presets
    quality_settings = {
        "low": {"crf": "28", "preset": "fast"},
        "medium": {"crf": "23", "preset": "medium"},
        "high": {"crf": "18", "preset": "slow"}
    }
    
    settings = quality_settings.get(quality, quality_settings["medium"])
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-c:v", "libx264",
            "-crf", settings["crf"],
            "-preset", settings["preset"],
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            compressed_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        
        return compressed_path
        
    except Exception as e:
        raise Exception(f"Video compression failed: {str(e)}")

def check_ffmpeg_installation():
    """
    Check if FFmpeg and FFprobe are properly installed
    
    Returns:
        dict: Status of FFmpeg tools installation
    """
    tools_status = {
        'ffmpeg': False,
        'ffprobe': False,
        'all_available': False
    }
    
    # Check ffmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=10)
        tools_status['ffmpeg'] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        tools_status['ffmpeg'] = False
    
    # Check ffprobe
    try:
        result = subprocess.run(["ffprobe", "-version"], 
                              capture_output=True, text=True, timeout=10)
        tools_status['ffprobe'] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        tools_status['ffprobe'] = False
    
    tools_status['all_available'] = tools_status['ffmpeg'] and tools_status['ffprobe']
    
    return tools_status
