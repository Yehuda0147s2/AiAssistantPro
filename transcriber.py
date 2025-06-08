import os
import tempfile
from openai import OpenAI

def transcribe_video(audio_path, output_dir):
    """
    Transcribe audio file using OpenAI Whisper API
    
    Args:
        audio_path (str): Path to the audio file
        output_dir (str): Directory to save the SRT file
    
    Returns:
        str: Path to the generated SRT file
    """
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Transcribe audio file
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt"  # Request SRT format directly
            )
        
        # Save SRT file
        srt_filename = os.path.join(output_dir, "transcription.srt")
        with open(srt_filename, "w", encoding="utf-8") as srt_file:
            srt_file.write(transcript)
        
        return srt_filename
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def transcribe_with_timestamps(audio_path, output_dir):
    """
    Transcribe audio with detailed timestamps
    
    Args:
        audio_path (str): Path to the audio file
        output_dir (str): Directory to save the output
    
    Returns:
        dict: Transcription data with timestamps
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return transcript
        
    except Exception as e:
        raise Exception(f"Detailed transcription failed: {str(e)}")

def format_srt_timestamp(seconds):
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds (float): Time in seconds
    
    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_srt_from_segments(segments, output_path):
    """
    Create SRT file from transcript segments
    
    Args:
        segments (list): List of transcript segments with timestamps
        output_path (str): Path to save the SRT file
    
    Returns:
        str: Path to the created SRT file
    """
    try:
        with open(output_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(segments, 1):
                start_time = format_srt_timestamp(segment['start'])
                end_time = format_srt_timestamp(segment['end'])
                text = segment['text'].strip()
                
                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{text}\n\n")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to create SRT file: {str(e)}")

def validate_audio_file(audio_path):
    """
    Validate audio file for transcription
    
    Args:
        audio_path (str): Path to the audio file
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(audio_path):
        return False
    
    # Check file size (OpenAI has a 25MB limit)
    file_size = os.path.getsize(audio_path)
    if file_size > 25 * 1024 * 1024:  # 25MB in bytes
        return False
    
    # Check file extension (basic validation)
    valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    file_ext = os.path.splitext(audio_path)[1].lower()
    
    return file_ext in valid_extensions
