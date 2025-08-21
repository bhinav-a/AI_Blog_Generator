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

    def extract_clean_paragraphs(self, soup):
    
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
            element.decompose()
        
        # Remove common ad/navigation classes
        ad_classes = ['ad', 'advertisement', 'sidebar', 'navigation', 'nav', 'menu', 'footer', 'header']
        for class_name in ad_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in str(x).lower()):
                element.decompose()
        
        # Extract paragraphs
        paragraphs = soup.find_all('p')
        clean_paragraphs = []
        
        for p in paragraphs:
            text = p.get_text().strip()
            # Filter out short, likely non-content paragraphs
            if len(text) > 20 and not self.is_likely_navigation(text):
                clean_paragraphs.append(text)
        
        return clean_paragraphs

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
        # Count words only from main content areas, not navigation
        main_content = self.extract_main_content(soup)
        words = main_content.split()
        return len(words)
    
    def is_likely_navigation(self, text):
        """Check if text is likely navigation/menu content"""
        nav_keywords = [
            'home', 'about', 'contact', 'login', 'register', 'subscribe',
            'menu', 'navigation', 'skip to', 'breadcrumb', 'previous', 'next',
            'share on', 'follow us', 'copyright', '©', 'privacy policy',
            'terms of service', 'cookie policy', 'all rights reserved'
        ]
        
        text_lower = text.lower()
        
        # Check for navigation keywords
        if any(keyword in text_lower for keyword in nav_keywords):
            return True
            
        # Check if text is very short (likely navigation)
        if len(text.split()) < 4:
            return True
            
        # Check if text is mostly links/navigation patterns
        if text.count('|') > 2 or text.count('»') > 0 or text.count('→') > 0:
            return True
            
        return False