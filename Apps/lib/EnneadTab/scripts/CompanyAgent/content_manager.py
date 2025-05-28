"""
Content Manager for EnneadTabAgent

This module handles:
- Web scraping the Ennead website
- Content processing and normalization
- Knowledge base updating
"""

import os
import sys
import json
import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import threading
import time

from . import constants
from . import utils
from . import vector_store

# Setup logger
logger = logging.getLogger("EnneadTabAgent.content_manager")

class ContentManager:
    def __init__(self, vector_store_instance=None):
        """Initialize the content manager."""
        self.vector_store = vector_store_instance
        self.base_url = constants.BASE_URL
        self.max_pages = constants.MAX_PAGES
        self.max_depth = constants.MAX_DEPTH
        self.urls_to_visit = constants.URLS_TO_VISIT.copy()
        self.visited_urls = set()
        self.skipped_urls = set()
        self.content = []
        self.crawl_details = {
            "start_time": None,
            "end_time": None,
            "pages_visited": 0,
            "pages_skipped": 0,
            "total_content_chunks": 0
        }
        self.content_cache_path = utils.get_storage_path("ennead_content.json")
        
    def initialize(self, force_update=False):
        """Initialize content by loading from cache or fetching new content."""
        try:
            # Try to load cached content first (if not forcing update)
            if not force_update and self._load_cached_content():
                logger.info("Successfully loaded cached content")
                return True
                
            # If no cached content or forcing update, fetch new content
            logger.info("Fetching new content from website...")
            if self.parse_website():
                # Cache the new content
                self._cache_content()
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error initializing content: {e}")
            return False
            
    def _load_cached_content(self):
        """Load content from cached file if it exists and is not too old."""
        try:
            if not os.path.exists(self.content_cache_path):
                logger.info(f"Content cache not found at {self.content_cache_path}")
                return False
                
            # Check age of cache
            file_time = datetime.fromtimestamp(os.path.getmtime(self.content_cache_path))
            max_age = constants.VECTOR_STORE_MAX_AGE_DAYS
            
            if (datetime.now() - file_time).days > max_age:
                logger.info(f"Content cache is older than {max_age} days, will create a new one")
                return False
                
            # Load cached content
            with open(self.content_cache_path, "r") as f:
                data = json.load(f)
                self.content = data.get("content", [])
                self.crawl_details = data.get("crawl_details", {})
                
            if not self.content:
                logger.warning("Cached content was empty")
                return False
                
            logger.info(f"Loaded {len(self.content)} content chunks from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading cached content: {e}")
            return False
            
    def _cache_content(self):
        """Cache the content to a file."""
        try:
            cache_data = {
                "content": self.content,
                "crawl_details": self.crawl_details,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.content_cache_path, "w") as f:
                json.dump(cache_data, f)
                
            logger.info(f"Cached {len(self.content)} content chunks to {self.content_cache_path}")
            return True
        except Exception as e:
            logger.error(f"Error caching content: {e}")
            return False
            
    def parse_website(self, focus_query=None):
        """Parse the Ennead website and extract content."""
        try:
            # Reset data
            self.visited_urls = set()
            self.skipped_urls = set()
            self.content = []
            
            # Record start time
            self.crawl_details["start_time"] = datetime.now().isoformat()
            
            def normalize_url(url, base):
                """Normalize URL to absolute form."""
                if url.startswith('/'):
                    return base.rstrip('/') + url
                elif url.startswith('http'):
                    return url
                else:
                    return base.rstrip('/') + '/' + url
                    
            def should_follow_link(url):
                """Determine if a link should be followed."""
                # Don't follow external links
                if not url.startswith(self.base_url):
                    return False
                    
                # Skip file downloads
                if any(url.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.jpg', '.png', '.zip']):
                    return False
                    
                # Skip certain paths
                skip_patterns = ['/search', '/login', '/admin', '/wp-admin', '/logout']
                if any(pattern in url for pattern in skip_patterns):
                    return False
                    
                return True
                
            def extract_content(soup, page_url):
                """Extract content from a BeautifulSoup parsed page."""
                page_content = []
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "Untitled Page"
                
                # Extract main content based on common content containers
                content_containers = soup.select('main, article, .content, #content, .main-content, .page-content')
                
                # If no specific content containers found, use body
                if not content_containers:
                    content_containers = [soup.find('body')]
                    
                for container in content_containers:
                    if not container:
                        continue
                        
                    # Skip navigation, footer, sidebars, etc.
                    for element in container.select('nav, footer, header, .sidebar, .navigation, .menu, .comments, script, style'):
                        if element:
                            element.decompose()
                            
                    # Extract text
                    text = container.get_text(separator=' ', strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        item = {
                            "url": page_url,
                            "title": title_text,
                            "text": text,
                            "source": "Ennead Website",
                            "timestamp": datetime.now().isoformat()
                        }
                        page_content.append(item)
                
                return page_content
                
            # Recursive function to parse pages
            def parse_page(url, depth=0):
                if url in self.visited_urls or url in self.skipped_urls:
                    return
                    
                if len(self.visited_urls) >= self.max_pages:
                    self.skipped_urls.add(url)
                    return
                    
                if depth > self.max_depth:
                    self.skipped_urls.add(url)
                    return
                    
                # Add to visited set
                self.visited_urls.add(url)
                logger.info(f"Parsing page {len(self.visited_urls)}: {url}")
                
                try:
                    # Request page with reasonable timeout
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        logger.warning(f"Error status {response.status_code} for {url}")
                        return
                        
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract content
                    page_content = extract_content(soup, url)
                    self.content.extend(page_content)
                    
                    # Extract links for further crawling
                    links = soup.find_all('a', href=True)
                    new_urls = []
                    
                    for link in links:
                        href = link['href']
                        abs_url = normalize_url(href, self.base_url)
                        
                        if should_follow_link(abs_url):
                            new_urls.append(abs_url)
                            
                    # Continue crawling
                    for new_url in new_urls:
                        parse_page(new_url, depth + 1)
                        
                except Exception as e:
                    logger.error(f"Error parsing {url}: {e}")
                    
            # Start parsing from the initial URLs
            for start_url in self.urls_to_visit:
                parse_page(start_url)
                
            # Record crawl details
            self.crawl_details["end_time"] = datetime.now().isoformat()
            self.crawl_details["pages_visited"] = len(self.visited_urls)
            self.crawl_details["pages_skipped"] = len(self.skipped_urls)
            self.crawl_details["total_content_chunks"] = len(self.content)
            
            logger.info(f"Website parsing complete. Visited {len(self.visited_urls)} pages, extracted {len(self.content)} content chunks.")
            
            return len(self.content) > 0
            
        except Exception as e:
            logger.error(f"Error parsing website: {e}")
            return False
            
    def process_to_vector_store(self):
        """Process content and add to vector store."""
        try:
            if not self.content:
                logger.warning("No content to process")
                return False
                
            if not self.vector_store:
                logger.error("No vector store available")
                return False
                
            # Prepare texts and metadata
            texts = []
            metadatas = []
            
            for item in self.content:
                texts.append(item["text"])
                metadatas.append({
                    "source": item.get("source", "Unknown"),
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "timestamp": item.get("timestamp", datetime.now().isoformat())
                })
                
            # Process and add to vector store
            documents = self.vector_store.process_text(texts, metadatas)
            
            if not documents:
                logger.warning("No documents created during processing")
                return False
                
            success = self.vector_store.update_vector_store(documents)
            
            if success:
                logger.info(f"Successfully added {len(documents)} documents to vector store")
            else:
                logger.warning("Failed to update vector store")
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing content to vector store: {e}")
            return False
            
    def update_knowledge_base(self, force_update=False):
        """Update the knowledge base with fresh content."""
        try:
            # Initialize content
            if not self.initialize(force_update):
                logger.warning("Failed to initialize content")
                return False
                
            # Process to vector store
            if not self.process_to_vector_store():
                logger.warning("Failed to process content to vector store")
                return False
                
            logger.info("Knowledge base updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            return False
            
    def update_knowledge_base_async(self, callback=None, force_update=False):
        """Update knowledge base in a background thread."""
        def update_thread():
            success = self.update_knowledge_base(force_update)
            if callback:
                callback(success)
                
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        return thread 