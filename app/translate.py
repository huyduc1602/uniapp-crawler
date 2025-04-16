import os
from bs4 import BeautifulSoup
import deepl
import googletrans
from dotenv import load_dotenv

load_dotenv()
auth_key = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(auth_key)

# Check if Google Translate API should be used
use_google_translate = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"
translator_google = googletrans.Translator() if use_google_translate else None

input_folder = "data/zh"
output_folder = "data/vi"
os.makedirs(output_folder, exist_ok=True)

# Function to translate text using the selected API
def translate_text(text, source_lang, target_lang):
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

for filename in os.listdir(input_folder):
    if filename.endswith(".html"):
        output_file_path = f"{output_folder}/{filename}"
        
        try:
            with open(f"{input_folder}/{filename}", "r", encoding="utf-8") as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            body_text = soup.get_text()

            print(f"Translating: {filename}")
            result, success = translate_text(body_text, source_lang="ZH", target_lang="VI")
            
            if success and result:
                # Only create the file if translation was successful
                with open(output_file_path, "w", encoding="utf-8") as out:
                    out.write(result)
                print(f"Successfully translated and saved: {filename}")
            else:
                # If translation failed and file exists, delete it
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)
                    print(f"Translation failed, deleted file: {filename}")
                else:
                    print(f"Translation failed, no file was created for: {filename}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            # If any error occurs and file exists, delete it
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
                print(f"Error occurred, deleted file: {filename}")
