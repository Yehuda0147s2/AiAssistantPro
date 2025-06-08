import os
import tempfile
import shutil
import time
from pathlib import Path
import json

def create_temp_dir():
    """
    Create a temporary directory for processing files
    
    Returns:
        str: Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix="youngaivagent_")
    return temp_dir

def cleanup_temp_files(temp_dirs):
    """
    Clean up temporary directories and files
    
    Args:
        temp_dirs (list): List of temporary directory paths to clean up
    """
    for temp_dir in temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up {temp_dir}: {e}")

def format_time(seconds):
    """
    Format seconds into human-readable time string
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string (HH:MM:SS)
    """
    if seconds < 0:
        return "Invalid time"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def get_file_size_mb(file_path):
    """
    Get file size in megabytes
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def validate_file_extension(filename, allowed_extensions):
    """
    Validate if file has an allowed extension
    
    Args:
        filename (str): Name of the file
        allowed_extensions (list): List of allowed extensions (with dots)
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]

def ensure_directory_exists(directory_path):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path (str): Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)

def safe_filename(filename):
    """
    Create a safe filename by removing/replacing problematic characters
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename
    """
    # Replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = f"file_{int(time.time())}"
    
    return safe_name

def read_text_file(file_path, encoding='utf-8'):
    """
    Safely read a text file
    
    Args:
        file_path (str): Path to the text file
        encoding (str): File encoding (default: utf-8)
        
    Returns:
        str: File content or empty string if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def write_text_file(content, file_path, encoding='utf-8'):
    """
    Safely write content to a text file
    
    Args:
        content (str): Content to write
        file_path (str): Path where to write the file
        encoding (str): File encoding (default: utf-8)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        ensure_directory_exists(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False

def log_processing_step(message, log_file=None):
    """
    Log processing steps with timestamp
    
    Args:
        message (str): Message to log
        log_file (str): Optional log file path
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    print(log_message)
    
    if log_file:
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")

def get_available_languages():
    """
    Get list of available translation languages
    
    Returns:
        dict: Dictionary mapping language names to codes
    """
    return {
        "Hebrew": "he",
        "Spanish": "es", 
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Arabic": "ar",
        "Russian": "ru",
        "Chinese": "zh",
        "Japanese": "ja",
        "Korean": "ko",
        "Dutch": "nl",
        "Swedish": "sv",
        "Norwegian": "no",
        "Danish": "da"
    }

def estimate_processing_time(video_duration_seconds, num_languages=1):
    """
    Estimate total processing time based on video duration and number of languages
    
    Args:
        video_duration_seconds (float): Video duration in seconds
        num_languages (int): Number of target languages
        
    Returns:
        dict: Estimated times for each step
    """
    # Rough estimates based on typical processing times
    transcription_time = video_duration_seconds * 0.1  # ~10% of video length
    translation_time_per_lang = video_duration_seconds * 0.05  # ~5% per language
    burning_time_per_lang = video_duration_seconds * 0.3  # ~30% per language
    
    total_translation_time = translation_time_per_lang * num_languages
    total_burning_time = burning_time_per_lang * num_languages
    
    total_time = transcription_time + total_translation_time + total_burning_time
    
    return {
        'transcription': transcription_time,
        'translation': total_translation_time,
        'burning': total_burning_time,
        'total': total_time,
        'formatted_total': format_time(total_time)
    }

def create_processing_summary(video_path, target_languages, output_files):
    """
    Create a summary of the processing results
    
    Args:
        video_path (str): Path to original video
        target_languages (list): List of target languages
        output_files (dict): Dictionary of output file paths
        
    Returns:
        dict: Processing summary
    """
    summary = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'original_video': {
            'path': video_path,
            'filename': os.path.basename(video_path),
            'size_mb': get_file_size_mb(video_path)
        },
        'target_languages': target_languages,
        'output_files': {},
        'total_files_created': 0,
        'total_output_size_mb': 0
    }
    
    for file_type, files in output_files.items():
        summary['output_files'][file_type] = {}
        for lang, file_path in files.items():
            if os.path.exists(file_path):
                file_size = get_file_size_mb(file_path)
                summary['output_files'][file_type][lang] = {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size_mb': file_size
                }
                summary['total_files_created'] += 1
                summary['total_output_size_mb'] += file_size
    
    return summary

def save_processing_summary(summary, output_dir):
    """
    Save processing summary as JSON file
    
    Args:
        summary (dict): Processing summary dictionary
        output_dir (str): Directory to save the summary
        
    Returns:
        str: Path to the saved summary file
    """
    summary_file = os.path.join(output_dir, "processing_summary.json")
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        return summary_file
    except Exception as e:
        print(f"Could not save processing summary: {e}")
        return None
