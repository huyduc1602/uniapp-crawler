import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

BASE_URL = 'https://uniapp.dcloud.io/'
OUTPUT_DIR = 'data/zh'

visited = set()

def is_internal_link(href):
    return href and urlparse(href).netloc in ('', 'uniapp.dcloud.io')

def save_page(title, content):
    safe_title = title.replace('/', '_').replace(' ', '_')
    with open(f"{OUTPUT_DIR}/{safe_title}.html", "w", encoding='utf-8') as f:
        f.write(content)

def crawl_page(url):
    if url in visited:
        return
    print(f'Crawling: {url}')
    visited.add(url)

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.title.string if soup.title else "untitled"
    save_page(title, res.text)

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(BASE_URL, href)
        if is_internal_link(href) and full_url.startswith(BASE_URL):
            crawl_page(full_url)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl_page(BASE_URL)