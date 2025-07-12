import os
import logging
from pathlib import Path
from openai import OpenAI, APIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transcribe_video(audio_path: str, output_dir: str) -> str:
    """
    Transcribes an audio file using the OpenAI Whisper API and returns the result as an SRT file.
    
    Args:
        audio_path (str): The path to the input audio file.
        output_dir (str): The directory where the generated SRT file will be saved.
    
    Returns:
        str: The path to the generated SRT file.

    Raises:
        ValueError: If the OpenAI API key is not found in environment variables.
        FileNotFoundError: If the audio file does not exist.
        Exception: For API errors or other issues during transcription.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
    
    audio_file_path = Path(audio_path)
    if not audio_file_path.exists():
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    client = OpenAI(api_key=api_key)
    
    try:
        logging.info(f"Starting transcription for {audio_file_path.name}...")
        with open(audio_file_path, "rb") as audio_file:
            # Request transcription from OpenAI API in SRT format
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt"
            )
        
        # Save the SRT content to a file
        srt_path = Path(output_dir) / f"{audio_file_path.stem}_transcription.srt"
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(transcript_response)
        
        logging.info(f"Transcription successful. SRT file saved to: {srt_path}")
        return str(srt_path)
        
    except APIError as e:
        logging.error(f"OpenAI API error during transcription: {e}")
        raise Exception(f"Failed to transcribe due to an API error: {e.message}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during transcription: {e}")
        raise

def transcribe_with_timestamps(audio_path: str) -> dict:
    """
    Transcribes an audio file with detailed, word-level timestamps using Whisper API.
    
    Args:
        audio_path (str): The path to the audio file.
    
    Returns:
        dict: A dictionary containing the detailed transcription data.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        return transcript
        
    except Exception as e:
        logging.error(f"Detailed transcription failed: {e}")
        raise

def format_srt_timestamp(seconds: float) -> str:
    """
    Converts a time in seconds to the SRT timestamp format (HH:MM:SS,mmm).
    
    Args:
        seconds (float): The time in seconds.
    
    Returns:
        str: The formatted SRT timestamp.
    """
    millisecs = int((seconds % 1) * 1000)
    secs = int(seconds % 60)
    minutes = int((seconds % 3600) // 60)
    hours = int(seconds // 3600)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_srt_from_segments(segments: list, output_path: str) -> str:
    """
    Creates an SRT file from a list of transcript segments.
    
    Args:
        segments (list): A list of dictionaries, where each dict represents a segment
                         with 'start', 'end', and 'text' keys.
        output_path (str): The path to save the generated SRT file.
    
    Returns:
        str: The path to the created SRT file.
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
        logging.error(f"Failed to create SRT file from segments: {e}")
        raise

def validate_audio_file(audio_path: str) -> bool:
    """
    Validates an audio file for transcription suitability.
    
    Args:
        audio_path (str): The path to the audio file.
    
    Returns:
        bool: True if the file is valid, False otherwise.
    """
    audio_file = Path(audio_path)
    if not audio_file.exists():
        logging.warning(f"Validation failed: Audio file not found at {audio_path}")
        return False
    
    # Check file size (OpenAI's Whisper API has a 25MB limit)
    file_size_mb = audio_file.stat().st_size / (1024 * 1024)
    if file_size_mb > 25:
        logging.warning(f"Validation failed: File size ({file_size_mb:.2f}MB) exceeds 25MB limit.")
        return False
    
    # Check for a valid audio file extension
    valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mpga', '.mpeg', '.webm']
    if audio_file.suffix.lower() not in valid_extensions:
        logging.warning(f"Validation failed: File extension '{audio_file.suffix}' is not typical for Whisper.")
        return False
    
    logging.info(f"Audio file {audio_path} passed validation.")
    return True
