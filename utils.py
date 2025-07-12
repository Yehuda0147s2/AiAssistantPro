import os
import tempfile
import shutil
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- File and Directory Management ---

def create_temp_dir() -> str:
    """
    Creates a temporary directory for processing files.
    
    Returns:
        str: The absolute path to the created temporary directory.
    """
    temp_dir = tempfile.mkdtemp(prefix="youngaivagent_")
    logging.info(f"Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_files(temp_dirs: List[str]):
    """
    Removes a list of temporary directories and their contents.
    
    Args:
        temp_dirs (List[str]): A list of directory paths to be removed.
    """
    for temp_dir in temp_dirs:
        try:
            if Path(temp_dir).exists() and Path(temp_dir).is_dir():
                shutil.rmtree(temp_dir)
                logging.info(f"Successfully cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logging.warning(f"Could not clean up temporary directory {temp_dir}: {e}")

def ensure_directory_exists(directory_path: str):
    """
    Ensures that a directory exists, creating it if necessary.

    Args:
        directory_path (str): The path to the directory.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

# --- Data Formatting and Validation ---

def format_time(seconds: float) -> str:
    """
    Formats a duration in seconds into a human-readable HH:MM:SS string.
    
    Args:
        seconds (float): The duration in seconds.
        
    Returns:
        str: The formatted time string (e.g., "01:05:22" or "15:30").
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours > 0 else f"{minutes:02d}:{secs:02d}"

def get_file_size_mb(file_path: str) -> float:
    """
    Gets the size of a file in megabytes.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        float: The file size in MB, or 0.0 if the file doesn't exist.
    """
    try:
        return Path(file_path).stat().st_size / (1024 * 1024)
    except FileNotFoundError:
        return 0.0

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validates if a file has one of the allowed extensions.
    
    Args:
        filename (str): The name of the file.
        allowed_extensions (List[str]): A list of allowed extensions (e.g., ['.mp4', '.mov']).
        
    Returns:
        bool: True if the file extension is in the allowed list, False otherwise.
    """
    return Path(filename).suffix.lower() in [ext.lower() for ext in allowed_extensions]

def safe_filename(filename: str) -> str:
    """
    Sanitizes a filename by removing or replacing characters that are invalid in most filesystems.
    
    Args:
        filename (str): The original filename.

    Returns:
        str: A filesystem-safe filename.
    """
    unsafe_chars = r'<>:"/\\|?*'
    safe_name = "".join('_' if char in unsafe_chars else char for char in filename).strip()
    return safe_name or f"file_{int(time.time())}"

# --- Language and Processing ---

def get_available_languages() -> Dict[str, str]:
    """
    Returns a dictionary of available languages for translation.

    Returns:
        Dict[str, str]: A dictionary mapping full language names to their two-letter codes.
    """
    return {
        "Arabic": "ar", "Chinese": "zh", "Danish": "da", "Dutch": "nl",
        "French": "fr", "German": "de", "Hebrew": "he", "Italian": "it",
        "Japanese": "ja", "Korean": "ko", "Norwegian": "no", "Portuguese": "pt",
        "Russian": "ru", "Spanish": "es", "Swedish": "sv"
    }

def estimate_processing_time(video_duration_seconds: float, num_languages: int = 1) -> Dict[str, Any]:
    """
    Estimates the total processing time based on video duration and number of languages.
    
    Args:
        video_duration_seconds (float): The video's duration in seconds.
        num_languages (int, optional): The number of target languages for translation. Defaults to 1.
        
    Returns:
        Dict[str, Any]: A dictionary with estimated times for each step and a formatted total.
    """
    if video_duration_seconds <= 0:
        return {'transcription': 0, 'translation': 0, 'burning': 0, 'total': 0, 'formatted_total': '00:00'}

    # Rough estimates (can be fine-tuned)
    transcription_time = video_duration_seconds * 0.1  # 10% of video length
    translation_time = video_duration_seconds * 0.05 * num_languages
    burning_time = video_duration_seconds * 0.3 * (num_languages + 1) # +1 for English
    
    total_time = transcription_time + translation_time + burning_time
    
    return {
        'transcription': transcription_time,
        'translation': translation_time,
        'burning': burning_time,
        'total': total_time,
        'formatted_total': format_time(total_time)
    }

# --- Data I/O and Summarization ---

def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Safely reads content from a text file.
    
    Args:
        file_path (str): The path to the text file.
        encoding (str, optional): The file encoding. Defaults to 'utf-8'.
        
    Returns:
        str: The file content, or an empty string if an error occurs.
    """
    try:
        return Path(file_path).read_text(encoding=encoding)
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return ""

def write_text_file(content: str, file_path: str, encoding: str = 'utf-8') -> bool:
    """
    Safely writes content to a text file, creating parent directories if needed.
    
    Args:
        content (str): The content to write.
        file_path (str): The path where the file will be saved.
        encoding (str, optional): The file encoding. Defaults to 'utf-8'.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return True
    except Exception as e:
        logging.error(f"Error writing file {file_path}: {e}")
        return False

def create_processing_summary(video_path: str, target_languages: List[str], output_files: Dict) -> Dict:
    """
    Creates a dictionary summarizing the results of a processing job.
    
    Args:
        video_path (str): The path to the original video.
        target_languages (List[str]): The list of target languages.
        output_files (Dict): A dictionary of output files, categorized by type.
        
    Returns:
        Dict: A structured summary of the processing results.
    """
    summary = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'original_video': {
            'path': video_path,
            'filename': Path(video_path).name,
            'size_mb': get_file_size_mb(video_path)
        },
        'target_languages': target_languages,
        'output_files': {},
        'total_files_created': 0,
        'total_output_size_mb': 0.0
    }
    
    for file_type, files in output_files.items():
        summary['output_files'][file_type] = {}
        for lang, path in files.items():
            if Path(path).exists():
                size = get_file_size_mb(path)
                summary['output_files'][file_type][lang] = {
                    'path': path,
                    'filename': Path(path).name,
                    'size_mb': size
                }
                summary['total_files_created'] += 1
                summary['total_output_size_mb'] += size
    
    return summary

def save_processing_summary(summary: Dict, output_dir: str) -> str:
    """
    Saves a processing summary dictionary to a JSON file.
    
    Args:
        summary (Dict): The summary dictionary.
        output_dir (str): The directory to save the summary file in.
        
    Returns:
        str: The path to the saved summary file, or None if saving fails.
    """
    summary_file = Path(output_dir) / "processing_summary.json"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        logging.info(f"Processing summary saved to {summary_file}")
        return str(summary_file)
    except Exception as e:
        logging.error(f"Could not save processing summary: {e}")
        return None
