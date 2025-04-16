import os
from bs4 import BeautifulSoup, NavigableString
import deepl
from dotenv import load_dotenv
import time

# Use deep_translator instead of googletrans
# deep_translator is more stable with Google's API
try:
    from deep_translator import GoogleTranslator
    google_translator_available = True
except ImportError:
    google_translator_available = False
    print("Could not import deep_translator. To use Google Translate, install: pip install deep-translator")

load_dotenv()
auth_key = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(auth_key) if auth_key else None

# Set the default translation provider to DeepL instead of Google Translate
use_google_translate = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true" and google_translator_available
translator_google = GoogleTranslator(source='zh-CN', target='vi') if use_google_translate else None

input_folder = "data/zh"
output_folder = "data/vi"
os.makedirs(output_folder, exist_ok=True)

def translate_text(text, source_lang, target_lang):
    """
    Translate text using the selected API (Google or DeepL).
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        tuple: (translated_text, success_flag)
    """
    if not text or text.strip() == '':
        return text, True
        
    if use_google_translate:
        print("Using Google Translate API")
        try:
            # Ensure text is not too long to avoid API limits
            max_length = 5000
            if len(text) > max_length:
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
                translated_chunks = []
                for chunk in chunks:
                    translated_chunk = translator_google.translate(chunk)
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        return text, False
                return "".join(translated_chunks), True
            else:
                translated_text = translator_google.translate(text)
                if translated_text:
                    return translated_text, True
                else:
                    print("Google Translate returned None. Translation failed.")
                    return text, False
        except Exception as e:
            print(f"Google Translate API error: {e}. Translation failed.")
            return text, False
    else:
        print("Using DeepL API")
        if not translator:
            print("DeepL API key not found. Translation failed.")
            return text, False
            
        try:
            result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang).text
            return result, True
        except Exception as e:
            print(f"DeepL API error: {e}. Translation failed.")
            return text, False

def translate_html_element(element, source_lang, target_lang):
    """
    Translate text content of an HTML element while preserving the HTML structure.
    
    Args:
        element: BeautifulSoup element to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        BeautifulSoup element with translated content
    """
    if isinstance(element, NavigableString):
        if element.strip():
            translated_text, success = translate_text(str(element), source_lang, target_lang)
            if success and translated_text:
                return NavigableString(translated_text)
        return element
    
    # Process all child nodes
    for i, child in enumerate(list(element.children)):
        translated_child = translate_html_element(child, source_lang, target_lang)
        if translated_child is not child:
            child.replace_with(translated_child)
    
    return element

# Process each HTML file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".html"):
        output_file_path = f"{output_folder}/{filename}"
        
        try:
            with open(f"{input_folder}/{filename}", "r", encoding="utf-8") as f:
                html_content = f.read()

            print(f"Translating HTML structure: {filename}")
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Translate the body content while preserving HTML structure
            translated_soup = translate_html_element(soup, source_lang="ZH", target_lang="VI")
            
            # Save the translated HTML with preserved structure
            if translated_soup:
                with open(output_file_path, "w", encoding="utf-8") as out:
                    out.write(str(translated_soup))
                print(f"Successfully translated and saved: {filename}")
            else:
                # If translation failed and file exists, delete it
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)
                    print(f"Translation failed, deleted file: {filename}")
                else:
                    print(f"Translation failed, no file was created for: {filename}")
                    
            # Sleep to avoid hitting API rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            # If any error occurs and file exists, delete it
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
                print(f"Error occurred, deleted file: {filename}")
