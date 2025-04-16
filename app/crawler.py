import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from requests.exceptions import ChunkedEncodingError

# Base URL for the Uniapp documentation
BASE_URL = 'https://uniapp.dcloud.net.cn/'
# Directory to store the Chinese version of the documentation
OUTPUT_DIR = 'data/zh'

# Set to track visited URLs to avoid duplicates
visited = set()

def is_internal_link(href):
    """
    Check if a URL belongs to the target domain.
    
    Args:
        href: URL string to check
        
    Returns:
        bool: True if the URL is from the target domain
    """
    return href and urlparse(href).netloc in ('', 'uniapp.dcloud.io')

def save_page(title, content, url):
    """
    Save crawled content to a file.
    
    Args:
        title: Page title to use in filename
        content: HTML content to save
        url: Original URL of the page
        
    Returns:
        str: Path to the saved file
    """
    if url.rstrip('/') in ('https://uniapp.dcloud.net.cn', 'https://uniapp.dcloud.io'):
        # If it's a root path, name the file as index.html
        filename = "index"
    else:
        # Otherwise, use the title as filename
        filename = title.replace('/', '_').replace(' ', '_')
    
    file_path = f"{OUTPUT_DIR}/{filename}.html"
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def crawl_page(url, depth=0, max_depth=10):
    """
    Recursively crawl pages starting from the given URL.
    
    Args:
        url: Starting URL to crawl
        depth: Current recursion depth
        max_depth: Maximum depth to crawl
    """
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
        # Handle chunked encoding errors by retrying
        print(f"ChunkedEncodingError encountered for: {url}. Retrying...")
        time.sleep(1)
        return crawl_page(url, depth)
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.title.string if soup.title else "untitled"
    save_page(title, res.text, url)

    # Find and process all links on the page
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(BASE_URL, href)
        if is_internal_link(href) and full_url.startswith(BASE_URL):
            crawl_page(full_url, depth + 1)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl_page(BASE_URL)