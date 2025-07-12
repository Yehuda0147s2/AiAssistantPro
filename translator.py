import re
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
import requests

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Using a session for connection pooling and performance
SESSION = requests.Session()

# Language mapping for translation services
LANGUAGE_MAP: Dict[str, str] = {
    "Hebrew": "he", "Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Arabic": "ar", "Russian": "ru",
    "Chinese": "zh", "Japanese": "ja", "Korean": "ko", "Dutch": "nl"
}

def translate_text_libretranslate(text: str, target_lang: str, source_lang: str = "en") -> str:
    """
    Translates text using the public LibreTranslate API.
    
    Args:
        text (str): The text to be translated.
        target_lang (str): The target language code (e.g., 'es', 'fr').
        source_lang (str, optional): The source language code. Defaults to "en".
    
    Returns:
        str: The translated text, or the original text if translation fails.
    """
    url = "https://libretranslate.de/translate"
    payload = {"q": text, "source": source_lang, "target": target_lang, "format": "text"}
    
    try:
        response = SESSION.post(url, data=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("translatedText", text)
        
    except requests.exceptions.RequestException as e:
        logging.warning(f"LibreTranslate API failed: {e}. Attempting fallback.")
        return translate_text_fallback(text, target_lang, source_lang)
    except Exception as e:
        logging.error(f"An unexpected error occurred with LibreTranslate: {e}")
        return text

def translate_text_fallback(text: str, target_lang: str, source_lang: str = "en") -> str:
    """
    A fallback translation function using the MyMemory API.
    
    Args:
        text (str): The text to be translated.
        target_lang (str): The target language code.
        source_lang (str, optional): The source language code. Defaults to "en".
    
    Returns:
        str: The translated text, or the original if all attempts fail.
    """
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text[:499], "langpair": f"{source_lang}|{target_lang}"}

    try:
        response = SESSION.get(url, params=params, timeout=15)
        response.raise_for_status()
        result = response.json()
        if result.get("responseStatus") == 200:
            return result["responseData"]["translatedText"]
        logging.warning(f"Fallback translation failed with status: {result.get('responseStatus')}")
    except Exception as e:
        logging.error(f"Fallback translation API failed: {e}")
    
    return text

def parse_srt_file(srt_path: str) -> List[Dict[str, Any]]:
    """
    Parses an SRT file and extracts subtitle entries into a list of dictionaries.
    
    Args:
        srt_path (str): The path to the SRT file.
    
    Returns:
        List[Dict[str, Any]]: A list of subtitle entries.
    """
    if not Path(srt_path).exists():
        logging.error(f"SRT file not found at: {srt_path}")
        return []

    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regex to split SRT file into blocks of index, timestamp, and text
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                subtitles.append({
                    'index': int(lines[0]),
                    'timestamp': lines[1],
                    'text': '\n'.join(lines[2:])
                })
            except (ValueError, IndexError) as e:
                logging.warning(f"Skipping malformed SRT block: {block} | Error: {e}")
    return subtitles

def create_translated_srt(subtitles: List[Dict[str, Any]], output_path: str) -> str:
    """
    Creates a new SRT file from a list of translated subtitle entries.
    
    Args:
        subtitles (List[Dict[str, Any]]): The list of subtitle entries.
        output_path (str): The path to save the new SRT file.
    
    Returns:
        str: The path to the created SRT file.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        for sub in subtitles:
            file.write(f"{sub['index']}\n")
            file.write(f"{sub['timestamp']}\n")
            file.write(f"{sub['text']}\n\n")
    return output_path

def translate_srt(srt_path: str, target_language: str, output_dir: str) -> str:
    """
    Translates an entire SRT file to a specified target language.
    
    Args:
        srt_path (str): The path to the source SRT file.
        target_language (str): The target language name (e.g., "Spanish").
        output_dir (str): The directory to save the translated SRT file.
    
    Returns:
        str: The path to the translated SRT file.

    Raises:
        ValueError: If the target language is not supported or subtitles cannot be parsed.
    """
    if target_language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: '{target_language}'.")
    
    target_lang_code = LANGUAGE_MAP[target_language]
    subtitles = parse_srt_file(srt_path)
    
    if not subtitles:
        raise ValueError("No valid subtitles found in the provided SRT file.")
    
    translated_subtitles = []
    total_subs = len(subtitles)
    
    for i, sub in enumerate(subtitles):
        clean_text = re.sub(r'<[^>]+>', '', sub['text']).strip()
        
        if clean_text:
            logging.info(f"Translating subtitle {i+1}/{total_subs} to {target_language}...")
            translated_text = translate_text_libretranslate(clean_text, target_lang_code)
            time.sleep(0.1)  # Small delay to avoid rate-limiting
        else:
            translated_text = sub['text']
        
        translated_subtitles.append({**sub, 'text': translated_text})
    
    # Construct the output path and save the new SRT file
    base_name = Path(srt_path).stem
    output_filename = f"{base_name}_{target_language.lower()}.srt"
    output_path = Path(output_dir) / output_filename
    
    return create_translated_srt(translated_subtitles, str(output_path))

def batch_translate_srt(srt_path: str, target_languages: List[str], output_dir: str) -> Dict[str, str]:
    """
    Translates an SRT file into multiple target languages.
    
    Args:
        srt_path (str): The path to the source SRT file.
        target_languages (List[str]): A list of target language names.
        output_dir (str): The directory to save the translated files.
    
    Returns:
        Dict[str, str]: A dictionary mapping language names to their SRT file paths.
    """
    translated_files = {}
    for lang in target_languages:
        try:
            translated_path = translate_srt(srt_path, lang, output_dir)
            translated_files[lang] = translated_path
            logging.info(f"Successfully translated to {lang}: {translated_path}")
        except Exception as e:
            logging.error(f"Failed to translate SRT to {lang}: {e}")
    return translated_files

def validate_translation_service() -> bool:
    """
    Validates that the primary translation service is accessible and working.
    
    Returns:
        bool: True if the service is accessible, False otherwise.
    """
    try:
        test_text = "Hello, world"
        translated = translate_text_libretranslate(test_text, "es")
        return translated.lower() == "hola, mundo"
    except Exception:
        return False
