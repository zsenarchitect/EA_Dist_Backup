import os
import sys
import json
import logging
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pickle

# Add DarkSide/exes/source code to path for _Exe_Util
current_dir = os.path.dirname(os.path.abspath(__file__))
darkside_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "DarkSide", "exes", "source code")
if darkside_path not in sys.path:
    sys.path.insert(0, darkside_path)

try:
    import _Exe_Util
except ImportError:
    print("Error: Could not import _Exe_Util module. Please make sure you're running from the correct directory.")
    print("Current directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)

def find_onedrive_desktop():
    """Find OneDrive Desktop folder by searching for 'OneDrive' in user's home directory."""
    home = os.path.expanduser("~")
    
    # Define possible desktop locations in order of preference
    possible_locations = [
        # OneDrive - Ennead paths
        os.path.join(home, "OneDrive - Ennead Architects", "Desktop"),
        os.path.join(home, "OneDrive - Ennead", "Desktop"),
        # Standard OneDrive paths
        os.path.join(home, "OneDrive", "Desktop"),
        # Regular Desktop
        os.path.join(home, "Desktop"),
        # Documents folder as fallback
        os.path.join(home, "Documents")
    ]
    
    # Check each location in order
    for location in possible_locations:
        if os.path.exists(location):
            print(f"Using desktop location: {location}")
            return location
    
    # Create Documents/Ennead folder as last resort
    fallback = os.path.join(home, "Documents", "Ennead")
    os.makedirs(fallback, exist_ok=True)
    print(f"Created and using fallback location: {fallback}")
    return fallback

class EnneadKnowledgeBase:
    def __init__(self):
        # Find desktop location for storing knowledge base
        desktop_path = find_onedrive_desktop()
        self.vector_store_path = os.path.join(desktop_path, "ennead_knowledge.pkl")
        self.knowledge_stats_path = os.path.join(desktop_path, "ennead_knowledge_stats.json")
        
        # Initialize properties
        self.vector_store = None
        self.api_key = None
        self.client = None
        self.pages_visited = {}
        
        # Setup logging
        self.setup_logging()
        
        # Log initialization
        logging.info(f"Initialized EnneadKnowledgeBase with vector store path: {self.vector_store_path}")
        
    def setup_logging(self):
        """Configure logging for the application."""
        log_file = "ennead_kb.log"
        
        try:
            # Create a formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            
            # Get the root logger
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            
            # Remove existing handlers to avoid duplicates
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                
            # Create handlers
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            logging.info("Logging initialized")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Set up basic logging as fallback
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        
    def get_knowledge_base_stats(self):
        """Get statistics about the knowledge base."""
        stats = {
            "last_updated": "Unknown",
            "chunk_count": 0,
            "page_count": 0,
            "sources": []
        }
        
        # Try to load stats from file
        if os.path.exists(self.knowledge_stats_path):
            try:
                with open(self.knowledge_stats_path, "r") as f:
                    stored_stats = json.load(f)
                    stats.update(stored_stats)
            except:
                pass
                
        # If we have a loaded vector store, update stats from it
        if self.vector_store:
            try:
                # Get document count
                stats["chunk_count"] = len(self.vector_store.index_to_docstore_id)
                
                # Count unique pages
                page_urls = set()
                sources = []
                for doc_id in self.vector_store.index_to_docstore_id.values():
                    doc = self.vector_store.docstore.search(doc_id)
                    if hasattr(doc, 'metadata') and 'url' in doc.metadata:
                        page_urls.add(doc.metadata['url'])
                        if doc.metadata['url'] not in sources:
                            sources.append(doc.metadata['url'])
                
                stats["page_count"] = len(page_urls)
                stats["sources"] = sources[:10]  # Limit to 10 sources for display
            except:
                pass
                
        return stats
        
    def save_knowledge_base_stats(self, content_dict=None):
        """Save statistics about the knowledge base."""
        stats = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chunk_count": 0,
            "page_count": 0,
            "sources": []
        }
        
        # Add crawl details if available
        if hasattr(self, 'crawl_details'):
            stats["crawl_details"] = self.crawl_details
        
        # If we have a loaded vector store, get stats from it
        if self.vector_store:
            try:
                # Get document count
                stats["chunk_count"] = len(self.vector_store.index_to_docstore_id)
                
                # Count unique pages
                page_urls = set()
                sources = []
                for doc_id in self.vector_store.index_to_docstore_id.values():
                    doc = self.vector_store.docstore.search(doc_id)
                    if hasattr(doc, 'metadata') and 'url' in doc.metadata:
                        page_urls.add(doc.metadata['url'])
                        if doc.metadata['url'] not in sources:
                            sources.append(doc.metadata['url'])
                
                stats["page_count"] = len(page_urls)
                stats["sources"] = sources[:10]  # Limit to 10 sources for display
            except:
                pass
        
        # If we have content dict from parsing, use that too
        if content_dict:
            try:
                stats["page_count"] = len(content_dict.get("pages", {}))
                stats["sources"] = list(content_dict.get("pages", {}).keys())[:10]
            except:
                pass
                
        # Save stats to file
        try:
            with open(self.knowledge_stats_path, "w") as f:
                json.dump(stats, f)
        except Exception as e:
            print(f"Error saving knowledge base stats: {e}")
            
        return stats
        
    def parse_website(self, focus_query=None):
        """Parse the Ennead website and extract content from all accessible pages."""
        try:
            base_url = "https://ei.ennead.com"
            alternative_urls = [
                "https://www.ennead.com",
                "https://ennead.com",
                "https://www.ennead.com/about",
                "https://www.ennead.com/projects",
                "https://www.ennead.com/services",
                "https://www.ennead.com/contact"
            ]
            
            # Add focus query related URLs if provided
            if focus_query:
                # Clean up query for search
                clean_query = focus_query.lower().replace(' ', '+')
                search_urls = [
                    f"https://www.ennead.com/search?q={clean_query}",
                    f"https://ei.ennead.com/search?q={clean_query}"
                ]
                alternative_urls = search_urls + alternative_urls
            
            visited_urls = set()
            self.pages_visited = {}  # Store pages that were successfully parsed
            
            # Start with base URL and alternatives
            queued_urls = [base_url] + alternative_urls
            
            content_dict = {
                "titles": [],
                "navigation": [],
                "main_content": [],
                "lists": [],
                "links": [],
                "metadata": [],
                "pages": {}  # Store page-specific content
            }
            
            def normalize_url(url, base):
                """Normalize URL to absolute form."""
                if not url:
                    return None
                # Remove fragments and query parameters
                url = url.split('#')[0].split('?')[0]
                # Handle different URL formats
                if url.startswith('//'):
                    return 'https:' + url
                if url.startswith('/'):
                    return base + url
                if not url.startswith('http'):
                    if url.startswith('./'):
                        url = url[2:]
                    return base + '/' + url
                return url

            def should_follow_link(url):
                """Determine if a link should be followed."""
                if not url:
                    return False
                # Skip common non-content URLs
                skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
                                 '.css', '.js', '.woff', '.woff2', '.ttf', '.eot']
                skip_patterns = ['mailto:', 'tel:', 'javascript:', '#', 'linkedin.com', 
                               'facebook.com', 'twitter.com', 'instagram.com']
                
                # Include all primary ennead.com domains
                ennead_domains = ['ennead.com', 'ei.ennead.com', 'www.ennead.com']
                
                # Check if URL is from an Ennead domain
                return not any(url.endswith(ext) for ext in skip_extensions) and \
                       not any(pattern in url for pattern in skip_patterns) and \
                       any(domain in url for domain in ennead_domains)

            def extract_content(soup, page_url):
                """Extract structured content from a page."""
                page_content = {
                    "title": "",
                    "headings": [],
                    "paragraphs": [],
                    "lists": [],
                    "links": [],
                    "metadata": {}
                }
                
                # Extract page title
                title_tag = soup.find('title')
                if title_tag and title_tag.text.strip():
                    page_title = title_tag.text.strip()
                    page_content["title"] = page_title
                    content_dict["titles"].append(f"[PAGE: {page_url}] {page_title}")
                
                # Extract meta tags
                for meta in soup.find_all('meta'):
                    name = meta.get('name', meta.get('property', ''))
                    content = meta.get('content', '')
                    if name and content:
                        page_content["metadata"][name] = content
                        content_dict["metadata"].append(f"[META: {name}] {content}")
                
                # Look for key content sections
                # 1. About section: Contains company information
                about_sections = soup.find_all(['section', 'div'], 
                                           class_=lambda c: c and any(keyword in str(c).lower() 
                                           for keyword in ['about', 'profile', 'company', 'team', 'firm', 'people']))
                
                # 2. Projects section: Contains project information
                project_sections = soup.find_all(['section', 'div'], 
                                             class_=lambda c: c and any(keyword in str(c).lower() 
                                             for keyword in ['project', 'work', 'portfolio']))
                
                # 3. Contact/Location section: Contains office information
                contact_sections = soup.find_all(['section', 'div'], 
                                             class_=lambda c: c and any(keyword in str(c).lower() 
                                             for keyword in ['contact', 'location', 'office', 'address']))
                
                # 4. Services section: Contains services information
                services_sections = soup.find_all(['section', 'div'], 
                                              class_=lambda c: c and any(keyword in str(c).lower() 
                                              for keyword in ['service', 'expertise', 'capability']))
                
                # Prioritize these sections
                priority_sections = []
                if 'about' in page_url.lower() or 'firm' in page_url.lower():
                    priority_sections.extend(about_sections)
                if 'project' in page_url.lower():
                    priority_sections.extend(project_sections)
                if 'contact' in page_url.lower() or 'location' in page_url.lower():
                    priority_sections.extend(contact_sections)
                if 'service' in page_url.lower():
                    priority_sections.extend(services_sections)
                
                # Combine all sections
                main_content_tags = priority_sections + about_sections + project_sections + contact_sections + services_sections
                
                # If no specific sections found, look for main content containers
                if not main_content_tags:
                    main_content_tags = soup.find_all(['article', 'main', 'section', 'div'], 
                                                  class_=lambda c: c and any(keyword in str(c).lower() 
                                                  for keyword in ['content', 'main', 'article', 'text']))
                
                # Fallback to body if still no content
                if not main_content_tags:
                    main_content_tags = [soup.find('body')]
                
                for content_container in main_content_tags:
                    if not content_container:
                        continue
                        
                    # Extract headings
                    for heading in content_container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        heading_text = heading.get_text(strip=True)
                        if heading_text:
                            tag_name = heading.name
                            page_content["headings"].append((tag_name, heading_text))
                            content_dict["titles"].append(f"[{tag_name}] {heading_text}")
                    
                    # Extract paragraphs
                    for para in content_container.find_all('p'):
                        para_text = para.get_text(strip=True)
                        if para_text and len(para_text) > 20:  # Skip very short paragraphs
                            page_content["paragraphs"].append(para_text)
                            content_dict["main_content"].append(para_text)
                    
                    # Extract lists
                    for list_el in content_container.find_all(['ul', 'ol']):
                        list_items = []
                        for item in list_el.find_all('li'):
                            item_text = item.get_text(strip=True)
                            if item_text:
                                list_items.append(item_text)
                        
                        if list_items:
                            list_type = 'ordered' if list_el.name == 'ol' else 'unordered'
                            page_content["lists"].append((list_type, list_items))
                            content_dict["lists"].extend(list_items)
                    
                    # Extract links with context
                    for link in content_container.find_all('a'):
                        link_text = link.get_text(strip=True)
                        href = link.get('href')
                        if link_text and href:
                            normalized_href = normalize_url(href, base_url)
                            if normalized_href:
                                page_content["links"].append((link_text, normalized_href))
                                content_dict["links"].append(f"{link_text} ({normalized_href})")
                                
                    # Try to find office addresses if this is a contact page
                    if 'contact' in page_url.lower():
                        # Look for address patterns in text
                        address_patterns = [
                            r"\d+\s+[\w\s]+,\s+[\w\s]+,\s+[A-Z]{2}\s+\d{5}",  # US address format
                            r"\d+\s+[\w\s]+,\s+[\w\s]+,\s+[A-Z]{2}",           # Shorter US format
                            r"\d+\s+[\w\s]+,\s+[\w\s]+"                       # Generic address format
                        ]
                        
                        for pattern in address_patterns:
                            import re
                            all_text = content_container.get_text()
                            addresses = re.findall(pattern, all_text)
                            if addresses:
                                for addr in addresses:
                                    special_content = f"[OFFICE ADDRESS] {addr}"
                                    if special_content not in content_dict["metadata"]:
                                        content_dict["metadata"].append(special_content)
                
                return page_content

            # Start crawling with BFS approach
            print(f"Starting website parsing with BFS traversal...")
            max_pages = 500  # Increased maximum page limit to 500
            
            # If focus query, log the focus
            if focus_query:
                print(f"Focusing crawl on query: '{focus_query}'")
                logging.info(f"Focused crawl initiated for query: '{focus_query}'")
                
            with requests.Session() as session:
                # Configure session
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5'
                })
                
                # BFS traversal
                while queued_urls and len(visited_urls) < max_pages:
                    current_url = queued_urls.pop(0)  # Get next URL from queue
                    
                    if current_url in visited_urls:
                        continue
                        
                    visited_urls.add(current_url)
                    print(f"Parsing page {len(visited_urls)}/{max_pages}: {current_url}")
                    
                    try:
                        response = session.get(current_url, timeout=15)
                        if response.status_code != 200:
                            print(f"  Error: HTTP {response.status_code}")
                            continue
                            
                        content_type = response.headers.get('Content-Type', '')
                        if 'text/html' not in content_type:
                            print(f"  Skipping: Not HTML content ({content_type})")
                            continue
                            
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Remove unwanted elements that might contain misleading links or content
                        for unwanted in soup.find_all(['script', 'style', 'noscript', 'iframe']):
                            unwanted.decompose()
                        
                        # Extract content from current page
                        page_content = extract_content(soup, current_url)
                        content_dict["pages"][current_url] = page_content
                        
                        # Find new links
                        for link in soup.find_all('a'):
                            href = link.get('href')
                            if href:
                                normalized_url = normalize_url(href, base_url)
                                if (normalized_url and 
                                    normalized_url not in visited_urls and 
                                    normalized_url not in queued_urls and
                                    should_follow_link(normalized_url)):
                                        queued_urls.append(normalized_url)
                        
                        # Rate limiting
                        if len(visited_urls) % 10 == 0:
                            import time
                            time.sleep(1)  # Be polite
                            
                    except requests.exceptions.Timeout:
                        print(f"  Timeout: {current_url}")
                        continue
                    except requests.exceptions.TooManyRedirects:
                        print(f"  Too many redirects: {current_url}")
                        continue
                    except requests.exceptions.RequestException as e:
                        print(f"  Request error: {e}")
                        continue
                    except Exception as e:
                        print(f"  Error processing {current_url}: {e}")
                        continue
            
            # Combine and format all content with section headers
            all_content = []
            
            if content_dict['titles']:
                all_content.extend(["=== Page Titles ==="] + content_dict['titles'])
            
            if content_dict['navigation']:
                all_content.extend(["=== Navigation ==="] + content_dict['navigation'])
            
            if content_dict['main_content']:
                all_content.extend(["=== Main Content ==="])
                # Group by page for context
                for url, page_data in content_dict["pages"].items():
                    if page_data["paragraphs"]:
                        all_content.append(f"\n--- Content from {url} ---")
                        all_content.extend(page_data["paragraphs"])
            
            if content_dict['lists']:
                all_content.extend(["=== Lists and Items ==="] + content_dict['lists'])
            
            if content_dict['links']:
                all_content.extend(["=== Links ==="] + content_dict['links'])
            
            if content_dict['metadata']:
                all_content.extend(["=== Metadata ==="] + content_dict['metadata'])
            
            if not any(content_dict.values()):
                print("No content found in website, using sample content for testing...")
                all_content = [
                    "=== About Ennead Architects ===",
                    "Ennead Architects is an internationally acclaimed architecture firm with offices in New York and Shanghai.",
                    "The firm is known for its innovative designs, cultural significance, and commitment to sustainable practices.",
                    
                    "=== Ennead Design Philosophy ===",
                    "Ennead's design approach centers on crafting spaces that engage with their cultural and physical context.",
                    "The firm values innovation, sustainability, and creating meaningful public spaces.",
                    "Each project is approached as a unique opportunity to create architecture that serves the needs of its users and community.",
                    
                    "=== Ennead Services ===",
                    "Architecture",
                    "Interior Design",
                    "Urban Planning",
                    "Master Planning",
                    "Sustainability Consulting",
                    "Historic Preservation",
                    
                    "=== Notable Projects ===",
                    "Shanghai Astronomy Museum",
                    "Natural History Museum of Utah",
                    "Stanford University Bing Concert Hall",
                    "Westmoreland Museum of American Art",
                    "University of Michigan Biological Sciences Building",
                    
                    "=== Office Locations ===",
                    "New York Office: 1 World Trade Center, New York, NY 10007",
                    "Shanghai Office: 83 Loushanguan Road, Shanghai, China"
                ]
            
            print(f"\nParsing Summary:")
            print(f"- Pages visited: {len(visited_urls)}")
            print(f"- Titles found: {len(content_dict['titles'])}")
            print(f"- Content sections: {len(content_dict['main_content'])}")
            print(f"- Lists/Items: {len(content_dict['lists'])}")
            print(f"- Links: {len(content_dict['links'])}")
            print(f"- Metadata items: {len(content_dict['metadata'])}")
            
            # Store successfully visited pages
            self.pages_visited = content_dict["pages"]
            
            # Store crawl details for stats
            self.crawl_details = {
                "pages_crawled": len(visited_urls),
                "focus_query": focus_query,
                "crawl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return "\n\n".join(all_content)
            
        except requests.exceptions.SSLError as e:
            print(f"SSL Error connecting to website: {e}")
            logging.error(f"SSL Error: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: {e}")
            logging.error(f"Connection Error: {e}")
            return None
        except Exception as e:
            print(f"Error parsing website: {e}")
            logging.error(f"Error parsing website: {e}")
            return None
            
    def process_content(self, content):
        """Process content and create vector embeddings."""
        if not content:
            print("No content to process")
            return
            
        # Get API key before processing
        print("Setting up OpenAI API key...")
        
        # Get or prompt for API key
        self.api_key = find_api_key()
        if not self.api_key:
            raise ValueError("Failed to obtain OpenAI API key")
            
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Improved content preprocessing
        print("Preprocessing content...")
        # Remove duplicate content and normalize whitespace
        lines = content.split('\n')
        unique_lines = []
        seen_content = set()
        for line in lines:
            clean_line = ' '.join(line.split())  # Normalize whitespace
            if clean_line and clean_line not in seen_content and len(clean_line) > 10:
                seen_content.add(clean_line)
                unique_lines.append(line)
        
        print(f"Removed {len(lines) - len(unique_lines)} duplicate/empty lines")
        preprocessed_content = '\n'.join(unique_lines)
        
        # More intelligent content chunking
        print("Splitting content into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(preprocessed_content)
        print(f"Created {len(chunks)} chunks")
        
        # Create embeddings with retry logic
        print("Generating embeddings...")
        embeddings = OpenAIEmbeddings(
            openai_api_key=self.api_key,
            model="text-embedding-3-small",  # Use efficient embedding model
            dimensions=1536  # Default dimension
        )
        
        # Create vector store with metadata and improved error handling
        print("Creating vector store...")
        try:
            # Add metadata to each chunk for better retrieval context
            documents = []
            for i, chunk in enumerate(chunks):
                # Extract section type from chunk if possible
                section_type = "unknown"
                if chunk.startswith("=== ") and " ===" in chunk:
                    section_type = chunk.split("=== ")[1].split(" ===")[0]
                
                # Create metadata
                metadata = {
                    "chunk_id": i,
                    "section_type": section_type,
                    "char_count": len(chunk),
                    "source": "ei.ennead.com",
                    "created_at": datetime.now().isoformat()
                }
                
                # If the chunk is from a specific URL, add it to metadata
                if "--- Content from " in chunk:
                    url_line = chunk.split("--- Content from ")[1].split("---")[0].strip()
                    metadata["url"] = url_line
                
                documents.append({"page_content": chunk, "metadata": metadata})
            
            # Create vector store from documents with metadata
            from langchain.schema import Document
            doc_objects = [
                Document(page_content=doc["page_content"], metadata=doc["metadata"]) 
                for doc in documents
            ]
            
            # Create FAISS vector store
            vector_store = FAISS.from_documents(doc_objects, embedding=embeddings)
            
            # Set the property
            self.vector_store = vector_store
            
            # Save vector store directly using FAISS's save_local method
            index_folder = os.path.join(os.path.dirname(self.vector_store_path), "ennead_knowledge_index")
            os.makedirs(index_folder, exist_ok=True)
            
            # Use save_local instead of pickle
            print(f"Saving vector store to {index_folder}...")
            self.vector_store.save_local(index_folder)
            
            # Save knowledge base stats
            print("Saving knowledge base stats...")
            stats = self.save_knowledge_base_stats({"pages": self.pages_visited if hasattr(self, 'pages_visited') else {}})
            
            print(f"Vector store created successfully with {len(chunks)} entries")
            print(f"Knowledge base last updated: {stats.get('last_updated', 'Unknown')}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error creating vector store: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            import traceback
            logging.error(traceback.format_exc())
            return False
            
    def load_vector_store(self):
        """Load existing vector store if available and not older than 7 days."""
        # Define index folder path
        index_folder = os.path.join(os.path.dirname(self.vector_store_path), "ennead_knowledge_index")
        
        # Check if vector store and stats exist
        stats_exist = os.path.exists(self.knowledge_stats_path)
        if stats_exist:
            try:
                # Check when the knowledge base was last updated
                with open(self.knowledge_stats_path, "r") as f:
                    stats = json.load(f)
                    last_updated = stats.get("last_updated", None)
                    
                    # If last_updated exists, check if it's within the 7-day threshold
                    if last_updated:
                        try:
                            # Parse the timestamp
                            last_update_time = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                            current_time = datetime.now()
                            
                            # Calculate age of vector store
                            age = current_time - last_update_time
                            max_age = timedelta(days=7)
                            
                            # If older than 7 days, log warning and return False to trigger regeneration
                            if age > max_age:
                                print(f"Vector store is {age.days} days old (older than 7 days threshold). Will regenerate.")
                                logging.info(f"Vector store age ({age.days} days) exceeds 7-day threshold. Regenerating.")
                                return False
                            else:
                                print(f"Vector store is {age.days} days old. Will reuse existing data.")
                                logging.info(f"Vector store age ({age.days} days) within threshold. Reusing.")
                        except Exception as e:
                            print(f"Error parsing timestamp: {e}. Will try to load anyway.")
                            logging.warning(f"Error parsing timestamp: {e}")
            except Exception as e:
                print(f"Error reading stats file: {e}")
                logging.warning(f"Error reading stats file: {e}")
        
        # Check if index folder exists
        if os.path.exists(index_folder):
            try:
                print(f"Loading vector store from {index_folder}...")
                
                # Get API key for embeddings
                api_key = find_api_key()
                if not api_key:
                    print("Cannot load vector store: No API key available")
                    return False
                    
                # Create embeddings
                embeddings = OpenAIEmbeddings(
                    openai_api_key=api_key,
                    model="text-embedding-3-small"
                )
                
                # Load vector store
                self.vector_store = FAISS.load_local(index_folder, embeddings)
                self.api_key = api_key
                
                print("Vector store loaded successfully")
                return True
                
            except Exception as e:
                print(f"Error loading vector store: {e}")
                import traceback
                logging.error(traceback.format_exc())
                return False
                
        # Fallback to legacy pickle format (for backward compatibility)
        if os.path.exists(self.vector_store_path) and self.vector_store_path.endswith('.pkl'):
            try:
                print(f"Loading vector store from {self.vector_store_path}...")
                with open(self.vector_store_path, "rb") as f:
                    self.vector_store = pickle.load(f)
                return True
            except Exception as e:
                print(f"Error loading vector store from pickle: {e}")
                return False
                
        # No vector store found
        print(f"No vector store found at {index_folder} or {self.vector_store_path}")
        return False
        
    def get_response(self, query):
        """Get response for user query using vector store and GPT-4."""
        if not self.vector_store:
            if self.load_vector_store():
                print("Successfully loaded existing knowledge base.")
            else:
                return "Knowledge base not initialized. Please parse the website first."
            
        # Get API key if not already set
        if not hasattr(self, 'api_key') or not self.api_key:
            try:
                # Get or prompt for API key
                self.api_key = find_api_key()
                if not self.api_key:
                    return "Error: Could not obtain a valid OpenAI API key"
            except Exception as e:
                return f"Error obtaining OpenAI API key: {str(e)}"
                
            # Initialize client
            self.client = OpenAI(api_key=self.api_key)
        
        try:
            # Clean and validate the query
            processed_query = query.strip()
            if not processed_query:
                return "Please enter a valid question."
                
            print(f"Processing query: {processed_query}")
            
            # Get relevant documents with metadata
            docs_with_scores = self.vector_store.similarity_search_with_score(processed_query, k=7)
            
            # Filter out low relevance documents and sort by relevance
            relevant_docs = [(doc, score) for doc, score in docs_with_scores if score < 0.9]
            relevant_docs.sort(key=lambda x: x[1])  # Sort by score (lower is better)
            
            if not relevant_docs:
                return "I couldn't find relevant information in my knowledge base to answer your question."
                
            # Format documents with metadata for context
            formatted_docs = []
            sources = set()
            
            for doc, score in relevant_docs:
                content = doc.page_content
                metadata = doc.metadata
                
                # Add source information if available
                source_info = ""
                if "url" in metadata:
                    source_url = metadata["url"]
                    sources.add(source_url)
                    source_info = f"[Source: {source_url}]"
                
                # Add section type if available
                section_type = ""
                if "section_type" in metadata and metadata["section_type"] != "unknown":
                    section_type = f"[Section: {metadata['section_type']}]"
                
                # Format the document with source info
                if source_info or section_type:
                    formatted_docs.append(f"{source_info} {section_type}\n{content}")
                else:
                    formatted_docs.append(content)
            
            # Create prompt with relevant context
            system_prompt = """You are a helpful assistant for Ennead Architects users. 
            Your purpose is to provide accurate, helpful information about Ennead Architects and their work.
            When answering:
            1. Be concise and direct
            2. If the information is clearly found in the context, answer confidently
            3. If you're unsure or the context doesn't contain the information, be honest about limitations
            4. Focus on being helpful and accurate rather than comprehensive
            5. Do not make up information not in the context
            6. When appropriate, offer suggestions for where the user might find more information
            """
            
            user_prompt = f"""Based on the following context from Ennead Architects resources, please answer this question:

Question: {processed_query}

Context:
{'-' * 30}
{'-' * 30}
{('\n' + '-' * 30 + '\n').join(formatted_docs)}
{'-' * 30}
"""
            
            # Get response from GPT-4
            print("Generating response...")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Add source attribution if we have sources
            if sources:
                source_list = "\n".join([f"- {src}" for src in sources])
                answer += f"\n\nSources:\n{source_list}"
            
            return answer
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            return f"Sorry, I encountered an error while generating a response. Error details: {str(e)}"

class ModernChatUI:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.chat_history = []
        self.username = self.get_username()
        self.setup_ui()
        
    def get_username(self):
        """Get the current user's Windows username."""
        try:
            import getpass
            username = getpass.getuser()
            # Format username nicely (capitalize first letter)
            if username:
                return username.split('.')[0].capitalize()
            return "Friend"
        except:
            return "Friend"
        
    def setup_ui(self):
        """Create modern dark-themed chat interface."""
        self.root = tk.Tk()
        self.root.title(f"{self.username}'s Ennead Architects Knowledge Chat")
        self.root.geometry("900x700")
        self.root.minsize(600, 400)
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#2C2F33"
        self.text_color = "#FFFFFF"
        self.accent_color = "#7289DA"
        self.input_bg = "#40444B"
        self.user_msg_bg = "#4F545C"
        self.system_msg_bg = "#36393F"
        self.assistant_msg_bg = "#7289DA"
        self.suggestion_bg = "#434960"
        self.link_color = "#00BFFF"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TButton", 
                       background=self.accent_color, 
                       foreground=self.text_color, 
                       borderwidth=0, 
                       font=("Segoe UI", 10, "bold"))
        style.map("TButton", 
                 background=[("active", "#677BC4"), ("disabled", "#4E5D94")])
        
        # Create header frame
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Logo/Title
        logo_label = ttk.Label(
            header_frame, 
            text=f"🧠 {self.username}'s Ennead Architects Knowledge Chat",
            background=self.bg_color,
            foreground=self.accent_color,
            font=("Segoe UI", 16, "bold")
        )
        logo_label.pack(side=tk.LEFT)
        
        # Parse website button
        self.parse_btn = ttk.Button(
            header_frame,
            text="🔄 Update Knowledge",
            command=self.update_knowledge
        )
        self.parse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add last updated timestamp if available
        self.timestamp_var = tk.StringVar()
        try:
            kb_stats = self.kb.get_knowledge_base_stats()
            last_updated = kb_stats.get("last_updated", "Unknown")
            self.timestamp_var.set(f"Last updated: {last_updated}")
        except:
            self.timestamp_var.set("")
            
        timestamp_label = ttk.Label(
            header_frame,
            textvariable=self.timestamp_var,
            background=self.bg_color,
            foreground="#AAAAAA",
            font=("Segoe UI", 9)
        )
        timestamp_label.pack(side=tk.RIGHT, padx=10)
        
        # Create main frame with chat and input areas
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Chat display with custom message rendering
        self.chat_frame = ttk.Frame(main_frame, style="TFrame")
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(
            self.chat_frame, 
            bg=self.bg_color,
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.chat_frame, 
            orient=tk.VERTICAL, 
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Messages container
        self.messages_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas_frame = self.canvas.create_window(
            (0, 0), 
            window=self.messages_frame, 
            anchor="nw"
        )
        
        # Configure canvas to resize with window
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Input area
        input_frame = ttk.Frame(main_frame, style="TFrame")
        input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Multiline message input with custom styling
        self.message_input = tk.Text(
            input_frame,
            font=("Segoe UI", 10),
            height=3,
            bg=self.input_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", self.check_shift_return)
        self.message_input.bind("<Control-Return>", self.send_message)
        
        # Placeholder text
        self.placeholder_text = "Type a message... (Press Enter to send, Shift+Enter for new line)"
        self.message_input.insert("1.0", self.placeholder_text)
        self.message_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.message_input.bind("<FocusOut>", self.on_entry_focus_out)
        
        # Send button with icon
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT, padx=(0, 0), pady=5)
        
        # Status bar
        self.status_frame = ttk.Frame(self.root, style="TFrame")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            background=self.bg_color,
            foreground="#AAAAAA",
            font=("Segoe UI", 8)
        )
        self.status_bar.pack(side=tk.LEFT)
        
        # Add welcome message with username
        self.add_message("system", f"Welcome, {self.username}! I'm your Ennead Architects knowledge assistant. Ask me anything about Ennead Architects, projects, or internal processes.")
        
        # Check if knowledge base is already loaded
        if hasattr(self.kb, 'vector_store') and self.kb.vector_store:
            self.add_message("system", "Knowledge base loaded and ready for your questions.")
            # Add suggested questions after a short delay
            self.root.after(500, self.show_suggested_questions)
        else:
            # Try to load existing knowledge base
            if self.kb.load_vector_store():
                self.add_message("system", "Knowledge base loaded successfully!")
                # Add suggested questions after a short delay
                self.root.after(500, self.show_suggested_questions)
            else:
                self.add_message("system", "No knowledge base found. Parsing website automatically...")
    
    def show_suggested_questions(self):
        """Show suggested questions that users can ask."""
        suggestions = [
            "What is Ennead Architects' design philosophy?",
            "Tell me about notable Ennead Architects projects",
            "What services does Ennead Architects offer?",
            "Where are Ennead Architects' offices located?",
            "How do I submit a PTO request?",
            "What is the process for expense reimbursement?",
            "How do I access the company VPN?",
            "What are the office working hours?"
        ]
        
        # Create suggestion frame
        suggest_frame = ttk.Frame(self.messages_frame, style="TFrame")
        suggest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create container
        suggest_container = tk.Frame(
            suggest_frame,
            bg=self.system_msg_bg,
            padx=10,
            pady=10,
            borderwidth=0,
            relief=tk.FLAT
        )
        suggest_container.pack(side=tk.LEFT, anchor="w", fill=tk.X, padx=5, pady=2)
        
        # Add title
        title_label = tk.Label(
            suggest_container,
            text=f"Hey {self.username}! Try asking me:",
            bg=self.system_msg_bg,
            fg=self.text_color,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            justify=tk.LEFT
        )
        title_label.pack(fill=tk.X, pady=(0, 5))
        
        # Create suggestion buttons
        for question in suggestions:
            # Button frame for styling
            btn_frame = tk.Frame(
                suggest_container,
                bg=self.suggestion_bg,
                padx=5,
                pady=5,
                borderwidth=0,
                relief=tk.FLAT
            )
            btn_frame.pack(fill=tk.X, pady=2)
            
            # Define command for this specific question
            def create_command(q):
                return lambda: self.ask_suggested_question(q)
                
            # Suggestion button
            btn = tk.Label(
                btn_frame,
                text=question,
                bg=self.suggestion_bg,
                fg=self.text_color,
                font=("Segoe UI", 9),
                cursor="hand2",
                anchor="w",
                padx=5,
                pady=5
            )
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, q=question: self.ask_suggested_question(q))
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn_frame: b.config(bg="#535C78"))
            btn.bind("<Leave>", lambda e, b=btn_frame: b.config(bg=self.suggestion_bg))
            
        # Auto-scroll to view suggestions
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def ask_suggested_question(self, question):
        """Ask a suggested question."""
        # Clear any placeholder text
        self.message_input.delete("1.0", tk.END)
        
        # Add the question to chat as user message
        self.add_message("user", question)
        
        # Process the question
        self.status_var.set("Thinking...")
        self.parse_btn.config(state=tk.DISABLED)
        self.root.update()
        
        # Get response in a separate thread
        threading.Thread(target=self.get_ai_response, args=(question,), daemon=True).start()
    
    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event=None):
        """When canvas is resized, also resize the messages frame and message containers"""
        # Resize the messages frame to match canvas width
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
        # Also update width of all message containers when window is resized
        for child in self.messages_frame.winfo_children():
            for container in child.winfo_children():
                if isinstance(container, tk.Frame):
                    container.config(width=int(event.width * 0.85))  # 85% of canvas width
    
    def on_entry_focus_in(self, event=None):
        """Clear placeholder text when entry gets focus"""
        if self.message_input.get("1.0", "end-1c") == self.placeholder_text:
            self.message_input.delete("1.0", tk.END)
            
    def on_entry_focus_out(self, event=None):
        """Add placeholder text if entry is empty and loses focus"""
        if not self.message_input.get("1.0", "end-1c").strip():
            self.message_input.delete("1.0", tk.END)
            self.message_input.insert("1.0", self.placeholder_text)
    
    def check_shift_return(self, event=None):
        """Handle Enter key press, allowing Shift+Enter for new line"""
        if event.state & 0x1:  # Shift is pressed
            return  # Allow default behavior (new line)
        else:
            self.send_message()
            return "break"  # Prevent default behavior
        
    def add_message(self, sender, message, return_frame=False):
        """Add a message to the chat display with appropriate styling."""
        # Create message frame
        msg_frame = ttk.Frame(self.messages_frame, style="TFrame")
        msg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Set background color based on sender
        if sender == "user":
            bg_color = self.user_msg_bg
            align = tk.RIGHT
            prefix = "You: "
        elif sender == "assistant":
            bg_color = self.assistant_msg_bg
            align = tk.LEFT
            prefix = "Assistant: "
        else:  # system
            bg_color = self.system_msg_bg
            align = tk.LEFT
            prefix = "System: "
            
        # Create message container with proper width
        container_width = int(self.canvas.winfo_width() * 0.85)  # Use 85% of canvas width
        msg_container = tk.Frame(
            msg_frame,
            bg=bg_color,
            padx=10,
            pady=5,
            borderwidth=0,
            relief=tk.FLAT,
            width=container_width
        )
        
        # Use pack with fill=X to ensure container expands properly
        if sender == "user":
            msg_container.pack(side=align, anchor="e", fill=tk.X, padx=5, pady=2, expand=False)
        else:
            msg_container.pack(side=align, anchor="w", fill=tk.X, padx=5, pady=2, expand=False)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add message text with wrapping
        msg_text = tk.Text(
            msg_container,
            wrap=tk.WORD,
            bg=bg_color,
            fg=self.text_color,
            width=50,  # Reduced width to prevent text being cut off
            relief=tk.FLAT,
            height=1,  # Will be adjusted based on content
            font=("Segoe UI", 10),
            padx=5,
            pady=5
        )
        msg_text.pack(fill=tk.BOTH, expand=True)
        
        # Add timestamp at top right
        msg_text.tag_configure("timestamp", foreground="#AAAAAA", justify=tk.RIGHT)
        msg_text.insert(tk.END, f"{timestamp}\n", "timestamp")
        
        # Configure content tags
        msg_text.tag_configure("content", spacing1=5, spacing3=5, lmargin1=2, lmargin2=2)
        msg_text.tag_configure("source", foreground="#AAAAAA", font=("Segoe UI", 8))
        
        # Insert actual message content
        msg_text.insert(tk.END, message, "content")
        
        # Adjust height based on content
        msg_text.config(state=tk.DISABLED)  # Make read-only
        line_count = int(msg_text.index('end-1c').split('.')[0])
        msg_text.config(height=min(15, max(2, line_count)))
        
        # Auto-scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
        # Add to chat history
        self.chat_history.append((sender, message))
        
        # Return the frame if requested (for adding buttons)
        if return_frame:
            return msg_frame
    
    def send_message(self, event=None):
        """Handle sending messages."""
        # Get message from input
        message = self.message_input.get("1.0", tk.END).strip()
        if not message or message == self.placeholder_text:
            return
            
        # Clear input
        self.message_input.delete("1.0", tk.END)
        
        # Add message to chat
        self.add_message("user", message)
        
        # Update status
        self.status_var.set("Thinking...")
        self.parse_btn.config(state=tk.DISABLED)
        self.root.update()
        
        # Get response in a separate thread
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
    
    def get_ai_response(self, message):
        """Get AI response in a separate thread."""
        try:
            response = self.kb.get_response(message)
            
            # Check if response contains any URLs or file paths
            urls = self.extract_urls(response)
            
            # If response indicates no information was found
            if "couldn't find relevant information" in response.lower() or "don't have information" in response.lower():
                # Ask if user wants to update knowledge base with this question
                follow_up_msg = "\n\nI don't have enough information about this topic in my knowledge base. " \
                               f"Would you like me to update my knowledge with a focus on '{message}'? " \
                               "This might help me answer similar questions in the future!"
                response += follow_up_msg
                
                # Add button to trigger knowledge update
                self.root.after(0, lambda: self.add_message_with_action(
                    "assistant", 
                    response, 
                    action_text="Update Knowledge", 
                    action_callback=lambda: self.update_knowledge_with_focus(message)
                ))
            elif urls:
                # If URLs were found, add option to open them
                self.root.after(0, lambda: self.add_message_with_links(
                    "assistant", 
                    response, 
                    urls
                ))
            else:
                # Regular response
                self.root.after(0, lambda: self.add_message("assistant", self.make_response_engaging(response)))
                
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, lambda: self.parse_btn.config(state=tk.NORMAL))
            
        except Exception as e:
            # Log the error with traceback
            import traceback
            error_traceback = traceback.format_exc()
            logging.error(f"Error generating response: {str(e)}")
            logging.error(f"Traceback: {error_traceback}")
            
            error_msg = f"Oops! I hit a snag while processing that: {str(e)}"
            self.root.after(0, lambda: self.add_message("system", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
            self.root.after(0, lambda: self.parse_btn.config(state=tk.NORMAL))
    
    def extract_urls(self, text):
        """Extract URLs and file paths from text."""
        urls = []
        
        # URL pattern
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        import re
        web_urls = re.findall(url_pattern, text)
        for url in web_urls:
            if not url.startswith('http'):
                url = 'https://' + url
            urls.append(('web', url))
        
        # File path pattern
        file_pattern = r'(?:\/|\\|[A-Za-z]:\\)[^\s<>"]*\.\w{2,4}'
        file_paths = re.findall(file_pattern, text)
        for path in file_paths:
            urls.append(('file', path))
            
        return urls
    
    def make_response_engaging(self, response):
        """Make the response more engaging and fun."""
        # Add some personality with occasional emoji and enthusiastic language
        import random
        
        emoji_options = ["✨", "🌟", "🎯", "💡", "🏆", "🔍", "📝", "🏢", "🌆", "📊"]
        enthusiasm_intros = [
            f"Great question, {self.username}! ",
            f"I'd be happy to help with that, {self.username}! ",
            f"Excellent inquiry, {self.username}! Here's what I found: ",
            f"Thanks for asking, {self.username}! ",
            f"I'm glad you asked that, {self.username}! "
        ]
        
        # Add an intro sometimes (30% chance)
        if random.random() < 0.3 and not response.startswith(f"{self.username}"):
            response = random.choice(enthusiasm_intros) + response
            
        # Add emoji sometimes (20% chance)
        if random.random() < 0.2 and not any(e in response for e in emoji_options):
            emoji = random.choice(emoji_options)
            # Add emoji at start or end
            if random.choice([True, False]):
                response = emoji + " " + response
            else:
                response = response + " " + emoji
                
        return response
    
    def add_message_with_action(self, sender, message, action_text, action_callback):
        """Add a message with an action button."""
        # First add the regular message
        msg_frame = self.add_message(sender, message, return_frame=True)
        
        # Add action button
        action_btn = ttk.Button(
            msg_frame,
            text=action_text,
            command=action_callback
        )
        action_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Auto-scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def add_message_with_links(self, sender, message, urls):
        """Add a message with clickable links."""
        # First add the regular message
        msg_frame = self.add_message(sender, message, return_frame=True)
        
        # Add link buttons for each URL
        for url_type, url in urls:
            # Create button frame
            link_frame = tk.Frame(
                msg_frame,
                bg=self.assistant_msg_bg,
                padx=5,
                pady=2
            )
            link_frame.pack(fill=tk.X, pady=2)
            
            # Create link label
            link_text = f"Open {url_type}: {url[:50]}..." if len(url) > 50 else f"Open {url_type}: {url}"
            link_label = tk.Label(
                link_frame,
                text=link_text,
                bg=self.assistant_msg_bg,
                fg=self.link_color,
                cursor="hand2",
                font=("Segoe UI", 9, "underline")
            )
            link_label.pack(side=tk.LEFT, padx=5)
            
            # Bind click action
            if url_type == 'web':
                link_label.bind("<Button-1>", lambda e, u=url: self.open_url(u))
            else:
                link_label.bind("<Button-1>", lambda e, p=url: self.open_file(p))
                
        # Auto-scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
    def open_url(self, url):
        """Open a URL in the default browser."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            self.add_message("system", f"Error opening URL: {str(e)}")
            
    def open_file(self, path):
        """Open a file with the default application."""
        try:
            import os
            import platform
            import subprocess
            
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            else:  # Linux
                subprocess.call(('xdg-open', path))
        except Exception as e:
            self.add_message("system", f"Error opening file: {str(e)}")
            
    def update_knowledge_with_focus(self, focus_query):
        """Update knowledge base with a focus on a specific query."""
        self.add_message("system", f"Starting to update the knowledge base with a focus on: '{focus_query}'. This may take a few minutes...")
        self.status_var.set("Parsing website...")
        self.parse_btn.config(state=tk.DISABLED)
        
        # Update timestamp display
        self.timestamp_var.set("Updating knowledge base...")
        
        self.root.update()
        
        # Run in separate thread
        threading.Thread(target=lambda: self._update_knowledge_thread(focus_query), daemon=True).start()
    
    def _update_knowledge_thread(self, focus_query=None):
        """Background thread for updating knowledge."""
        try:
            # Parse website with focus query if provided
            content = self.kb.parse_website(focus_query) if focus_query else self.kb.parse_website()
            if not content:
                self.root.after(0, lambda: self.add_message("system", "Failed to parse website. Please check your internet connection and try again."))
                self.root.after(0, lambda: self.status_var.set("Parse failed"))
                self.root.after(0, lambda: self.parse_btn.config(state=tk.NORMAL))
                return
                
            # Process content
            self.root.after(0, lambda: self.status_var.set("Creating knowledge base..."))
            self.kb.process_content(content)
            
            # Update timestamp
            kb_stats = self.kb.get_knowledge_base_stats()
            last_updated = kb_stats.get("last_updated", "Unknown")
            self.root.after(0, lambda: self.timestamp_var.set(f"Last updated: {last_updated}"))
            
            # Update UI with success message
            success_msg = "Knowledge base updated successfully! You can now ask questions."
            if focus_query:
                success_msg = f"Knowledge base updated successfully with a focus on '{focus_query}'! Try asking your question again."
            
            self.root.after(0, lambda: self.add_message("system", success_msg))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, lambda: self.parse_btn.config(state=tk.NORMAL))
            
        except Exception as e:
            # Log the error with traceback
            import traceback
            error_traceback = traceback.format_exc()
            logging.error(f"Error updating knowledge base: {str(e)}")
            logging.error(f"Traceback: {error_traceback}")
            
            error_msg = f"Error updating knowledge base: {str(e)}"
            self.root.after(0, lambda: self.add_message("system", error_msg))
            self.root.after(0, lambda: self.status_var.set("Update failed"))
            self.root.after(0, lambda: self.parse_btn.config(state=tk.NORMAL))
        
    def update_knowledge(self):
        """Parse website and update knowledge base."""
        self.update_knowledge_with_focus(None)
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()

def find_api_key():
    """Find or prompt for API key and save it for future use."""
    # Define the API key file path
    dump_folder = os.path.join(os.path.expanduser("~"), "Documents", "EnneadTab-Ecosystem", "Dump")
    os.makedirs(dump_folder, exist_ok=True)
    api_key_file = os.path.join(dump_folder, "EA_API_KEY.secret")
    
    # Try to load existing API key from file
    api_key = None
    if os.path.exists(api_key_file):
        try:
            with open(api_key_file, "r") as f:
                data = json.load(f)
                api_key = data.get("EnneadTabAPI")
                if api_key:
                    print(f"Using saved API key from: {api_key_file}")
                    return api_key
        except Exception as e:
            print(f"Error reading API key file: {e}")
    
    # If not found or invalid, prompt user
    print("No valid API key found. Prompting user...")
    
    # Create a simple UI to get the API key
    key_root = tk.Tk()
    key_root.title("Enter OpenAI API Key")
    key_root.geometry("500x200")
    key_root.configure(bg="#2C2F33")
    
    frame = ttk.Frame(key_root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    ttk.Label(
        frame, 
        text="Enter your OpenAI API Key:", 
        font=("Segoe UI", 12)
    ).pack(pady=(0, 10))
    
    # Entry for API key
    key_var = tk.StringVar()
    key_entry = ttk.Entry(frame, textvariable=key_var, width=50, show="•")
    key_entry.pack(fill=tk.X, pady=10)
    key_entry.focus()
    
    # Status message
    status_var = tk.StringVar()
    status_var.set("API key will be saved for future use")
    status_label = ttk.Label(frame, textvariable=status_var, font=("Segoe UI", 9))
    status_label.pack(pady=5)
    
    # Result variable to store the key
    result = {"key": None}
    
    def save_key():
        key = key_var.get().strip()
        if not key:
            status_var.set("Please enter a valid API key")
            return
            
        # Save the key to file
        try:
            with open(api_key_file, "w") as f:
                json.dump({"EnneadTabAPI": key}, f)
            status_var.set("API key saved successfully!")
            print(f"API key saved to: {api_key_file}")
        except Exception as e:
            status_var.set(f"Error saving key: {e}")
            print(f"Error saving key: {e}")
            
        result["key"] = key
        key_root.after(1000, key_root.destroy)  # Close after 1 second
        
    def cancel():
        key_root.destroy()
        
    # Buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(
        button_frame, 
        text="Save Key", 
        command=save_key
    ).pack(side=tk.RIGHT, padx=5)
    
    ttk.Button(
        button_frame, 
        text="Cancel", 
        command=cancel
    ).pack(side=tk.RIGHT, padx=5)
    
    # Handle Enter key
    key_entry.bind("<Return>", lambda event: save_key())
    
    # Center window
    key_root.update_idletasks()
    width = key_root.winfo_width()
    height = key_root.winfo_height()
    x = (key_root.winfo_screenwidth() // 2) - (width // 2)
    y = (key_root.winfo_screenheight() // 2) - (height // 2)
    key_root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Bring window to front
    key_root.attributes('-topmost', True)
    key_root.update()
    key_root.attributes('-topmost', False)
    
    # Run window
    key_root.mainloop()
    
    # Get the result
    api_key = result["key"]
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)
        
    return api_key

def main():
    try:
        # Print welcome message
        print("\n" + "=" * 60)
        print("Welcome to Ennead Architects Knowledge Chat")
        print("=" * 60)
        print("This application allows you to chat with Ennead Architects knowledge")
        print("sourced from the Ennead Architects website.")
        print("=" * 60 + "\n")
        
        print("1. Initializing knowledge base")
        
        # Initialize knowledge base
        kb = EnneadKnowledgeBase()
        
        print("2. Checking for existing knowledge base")
        # Try to load existing vector store
        kb_loaded = kb.load_vector_store()
        
        if kb_loaded:
            # Display when the knowledge base was last updated
            try:
                kb_stats = kb.get_knowledge_base_stats()
                last_updated = kb_stats.get("last_updated", "Unknown")
                chunk_count = kb_stats.get("chunk_count", 0)
                page_count = kb_stats.get("page_count", 0)
                
                print(f"✓ Knowledge base loaded successfully!")
                print(f"  Last updated: {last_updated}")
                print(f"  Contains {chunk_count} chunks from {page_count} pages")
            except Exception as e:
                logging.warning(f"Error getting knowledge base stats: {e}")
                print(f"✓ Knowledge base loaded successfully!")
        else:
            print("! No existing knowledge base found")
            print("  Automatically parsing website...")
            
            try:
                # Parse website content
                content = kb.parse_website()
                if content:
                    print("3. Processing website content...")
                    kb.process_content(content)
                    print("✓ Knowledge base created successfully!")
                else:
                    print("! Failed to parse website content.")
                    print("  Starting UI anyway with limited functionality...")
            except Exception as e:
                # Log the error but continue with UI
                import traceback
                error_traceback = traceback.format_exc()
                logging.error(f"Error creating knowledge base: {str(e)}")
                logging.error(f"Traceback: {error_traceback}")
                
                print(f"! Error creating knowledge base: {str(e)}")
                print("  Starting UI with limited functionality...")
        
        print("4. Starting chat UI...")
        print("-" * 60)
        
        # Start UI
        ui = ModernChatUI(kb)
        ui.run()
        
    except Exception as e:
        # Log detailed error with traceback
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Application error: {str(e)}")
        logging.error(f"Traceback: {error_traceback}")
        print(f"Error: {e}")
        print("Check the log file for detailed traceback.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Check for required Python version
        if sys.version_info < (3, 7):
            print("Error: Python 3.7 or higher is required.")
            sys.exit(1)
            
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("ennead_kb.log"),
                logging.StreamHandler()
            ]
        )
        
        # Run main function
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except Exception as e:
        # Log detailed error with traceback
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Unhandled exception: {str(e)}")
        logging.error(f"Traceback: {error_traceback}")
        print(f"Unhandled exception: {e}")
        print("Check the log file for detailed traceback.")
        sys.exit(1)
