import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import tempfile

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape(self):
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract various data points
            data = {
                'url': self.url,
                'title': self.extract_title(soup),
                'meta_description': self.extract_meta_description(soup),
                'headings': self.extract_headings(soup),
                'paragraphs': self.extract_paragraphs(soup),
                'links': self.extract_links(soup),
                'images': self.extract_images(soup),
                'meta_tags': self.extract_meta_tags(soup),
                'word_count': self.count_words(soup),
                'scraped_at': str(timezone.now())
            }
            
            return data, None
            
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"
        except Exception as e:
            return None, f"Scraping error: {str(e)}"

    def extract_title(self, soup):
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''

    def extract_meta_description(self, soup):
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ''

    def extract_headings(self, soup):
        headings = {}
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [tag.get_text().strip() for tag in heading_tags]
        return headings

    def extract_paragraphs(self, soup):
        paragraphs = soup.find_all('p')
        return [p.get_text().strip() for p in paragraphs if p.get_text().strip()]

    def extract_links(self, soup):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            absolute_url = urljoin(self.url, href)
            links.append({
                'text': text,
                'href': href,
                'absolute_url': absolute_url
            })
        return links

    def extract_images(self, soup):
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                absolute_url = urljoin(self.url, src)
                images.append({
                    'src': src,
                    'alt': alt,
                    'absolute_url': absolute_url
                })
        return images

    def extract_meta_tags(self, soup):
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        return meta_tags

    def count_words(self, soup):
        text = soup.get_text()
        words = text.split()
        return len(words)