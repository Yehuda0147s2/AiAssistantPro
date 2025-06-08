import os
import requests
import re
from pathlib import Path
import time

# Language mapping for LibreTranslate
LANGUAGE_MAP = {
    "Hebrew": "he",
    "Spanish": "es", 
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja"
}

def translate_text_libretranslate(text, target_lang, source_lang="en"):
    """
    Translate text using LibreTranslate API
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code
        source_lang (str): Source language code (default: en)
    
    Returns:
        str: Translated text
    """
    # Use public LibreTranslate instance
    url = "https://libretranslate.de/translate"
    
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("translatedText", text)
        
    except requests.exceptions.RequestException as e:
        # Fallback to a different service or return original text
        print(f"LibreTranslate failed: {e}")
        return translate_text_fallback(text, target_lang, source_lang)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_text_fallback(text, target_lang, source_lang="en"):
    """
    Fallback translation using alternative service
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code
        source_lang (str): Source language code
    
    Returns:
        str: Translated text or original if failed
    """
    try:
        # Alternative: MyMemory API (free tier)
        url = f"https://api.mymemory.translated.net/get"
        params = {
            "q": text[:500],  # Limit text length
            "langpair": f"{source_lang}|{target_lang}"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        if result.get("responseStatus") == 200:
            return result["responseData"]["translatedText"]
        
    except Exception as e:
        print(f"Fallback translation failed: {e}")
    
    return text  # Return original text if all translation attempts fail

def parse_srt_file(srt_path):
    """
    Parse SRT file and extract subtitle entries
    
    Args:
        srt_path (str): Path to the SRT file
    
    Returns:
        list: List of subtitle entries with index, timestamp, and text
    """
    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'index': index,
                    'timestamp': timestamp,
                    'text': text
                })
            except (ValueError, IndexError):
                continue
    
    return subtitles

def create_translated_srt(subtitles, output_path):
    """
    Create SRT file from translated subtitles
    
    Args:
        subtitles (list): List of subtitle entries
        output_path (str): Path to save the translated SRT file
    
    Returns:
        str: Path to the created SRT file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        for subtitle in subtitles:
            file.write(f"{subtitle['index']}\n")
            file.write(f"{subtitle['timestamp']}\n")
            file.write(f"{subtitle['text']}\n\n")
    
    return output_path

def translate_srt(srt_path, target_language, output_dir):
    """
    Translate an entire SRT file to target language
    
    Args:
        srt_path (str): Path to the source SRT file
        target_language (str): Target language name (e.g., "Hebrew", "Spanish")
        output_dir (str): Directory to save the translated SRT file
    
    Returns:
        str: Path to the translated SRT file
    """
    if target_language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {target_language}")
    
    target_lang_code = LANGUAGE_MAP[target_language]
    
    # Parse original SRT file
    subtitles = parse_srt_file(srt_path)
    
    if not subtitles:
        raise ValueError("No subtitles found in SRT file")
    
    # Translate each subtitle
    translated_subtitles = []
    
    for subtitle in subtitles:
        # Clean text for translation (remove formatting)
        clean_text = re.sub(r'<[^>]+>', '', subtitle['text'])
        clean_text = clean_text.strip()
        
        if clean_text:
            # Translate the text
            translated_text = translate_text_libretranslate(
                clean_text, 
                target_lang_code, 
                "en"
            )
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
        else:
            translated_text = subtitle['text']
        
        translated_subtitles.append({
            'index': subtitle['index'],
            'timestamp': subtitle['timestamp'],
            'text': translated_text
        })
    
    # Create output filename
    base_name = Path(srt_path).stem
    output_filename = f"{base_name}_{target_language.lower()}.srt"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save translated SRT file
    return create_translated_srt(translated_subtitles, output_path)

def batch_translate_srt(srt_path, target_languages, output_dir):
    """
    Translate SRT file to multiple target languages
    
    Args:
        srt_path (str): Path to the source SRT file
        target_languages (list): List of target language names
        output_dir (str): Directory to save translated SRT files
    
    Returns:
        dict: Dictionary mapping language names to translated SRT file paths
    """
    translated_files = {}
    
    for language in target_languages:
        try:
            translated_file = translate_srt(srt_path, language, output_dir)
            translated_files[language] = translated_file
        except Exception as e:
            print(f"Failed to translate to {language}: {e}")
            continue
    
    return translated_files

def validate_translation_service():
    """
    Validate that translation service is accessible
    
    Returns:
        bool: True if service is accessible, False otherwise
    """
    try:
        test_text = "Hello"
        translated = translate_text_libretranslate(test_text, "es", "en")
        return translated != test_text  # Should be different if translation worked
    except Exception:
        return False
