import os
from bs4 import BeautifulSoup, NavigableString
import deepl
import googletrans
from dotenv import load_dotenv
import time

load_dotenv()
auth_key = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(auth_key)

# Change the default translation provider to DeepL instead of Google Translate
use_google_translate = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"
translator_google = googletrans.Translator() if use_google_translate else None

input_folder = "data/zh"
output_folder = "data/vi"
os.makedirs(output_folder, exist_ok=True)

# Function to translate text using the selected API
def translate_text(text, source_lang, target_lang):
    if not text or text.strip() == '':
        return text, True
        
    if use_google_translate:
        print("Using Google Translate API")
        # Correct the language code for Google Translate
        source_lang = "zh-cn" if source_lang.lower() == "zh" else source_lang.lower()
        target_lang = target_lang.lower()
        try:
            translation = translator_google.translate(text, src=source_lang, dest=target_lang)
            if translation and translation.text:
                return translation.text, True
            else:
                print("Google Translate returned None. Translation failed.")
                return None, False
        except Exception as e:
            print(f"Google Translate API error: {e}. Translation failed.")
            return None, False
    else:
        print("Using DeepL API")
        try:
            result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang).text
            return result, True
        except Exception as e:
            print(f"DeepL API error: {e}. Translation failed.")
            return None, False

def translate_html_element(element, source_lang, target_lang):
    """Translate text content of an HTML element while preserving the HTML structure"""
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
