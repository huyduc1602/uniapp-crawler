import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from requests.exceptions import ChunkedEncodingError

BASE_URL = 'https://uniapp.dcloud.io/'
OUTPUT_DIR = 'data/zh'

visited = set()

def is_internal_link(href):
    return href and urlparse(href).netloc in ('', 'uniapp.dcloud.io')

def save_page(title, content):
    safe_title = title.replace('/', '_').replace(' ', '_')
    with open(f"{OUTPUT_DIR}/{safe_title}.html", "w", encoding='utf-8') as f:
        f.write(content)

def crawl_page(url, depth=0, max_depth=10):
    if depth > max_depth:
        print(f"Max depth reached for: {url}")
        return

    if url in visited:
        return

    # Check if the file already exists
    safe_title = url.split('/')[-1].replace('/', '_').replace(' ', '_')
    file_path = f"{OUTPUT_DIR}/{safe_title}.html"
    if os.path.exists(file_path):
        print(f"File already exists for URL: {url}, skipping crawl.")
        return

    print(f'Crawling: {url}')
    visited.add(url)

    try:
        res = requests.get(url)
        res.raise_for_status()
    except ChunkedEncodingError:
        print(f"ChunkedEncodingError encountered for: {url}. Retrying...")
        time.sleep(1)
        return crawl_page(url, depth)
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.title.string if soup.title else "untitled"
    save_page(title, res.text)

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(BASE_URL, href)
        if is_internal_link(href) and full_url.startswith(BASE_URL):
            crawl_page(full_url, depth + 1)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl_page(BASE_URL)