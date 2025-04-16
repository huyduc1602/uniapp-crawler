import os
from bs4 import BeautifulSoup
import deepl
from dotenv import load_dotenv

load_dotenv()
auth_key = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(auth_key)

input_folder = "data/zh"
output_folder = "data/vi"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".html"):
        with open(f"{input_folder}/{filename}", "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        body_text = soup.get_text()

        print(f"Translating: {filename}")
        result = translator.translate_text(body_text, source_lang="ZH", target_lang="VI")

        with open(f"{output_folder}/{filename}", "w", encoding="utf-8") as out:
            out.write(result.text)
