import os
import sys
import json
import logging
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
import getpass

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

# Constants
VECTOR_STORE_MAX_AGE_DAYS = 3
SUGGESTED_TOPICS = [
    "What are Ennead Architects' most notable projects?",
    "Tell me about Ennead's design philosophy",
    "What services does Ennead Architects offer?",
    "How can I contact Ennead Architects?",
    "What is Ennead's approach to sustainable design?"
]

def find_onedrive_desktop():
    """Find OneDrive Desktop folder by searching for 'OneDrive' in user's home directory."""
    home = os.path.expanduser("~")
    
    # Common OneDrive folder patterns
    patterns = [
        r"OneDrive - Ennead Architects\Desktop",  # Specific Ennead pattern
        r"OneDrive.*Desktop",
        r"OneDrive - .*Desktop",
        r"OneDrive.*\Desktop",
        r"OneDrive - .*\Desktop"
    ]
    
    # First try the most common Ennead path
    ennead_path = os.path.join(home, "OneDrive - Ennead Architects", "Desktop")
    if os.path.exists(ennead_path):
        return ennead_path
    
    # Search in home directory
    for root, dirs, files in os.walk(home):
        for dir_name in dirs:
            for pattern in patterns:
                if re.search(pattern, dir_name, re.IGNORECASE):
                    full_path = os.path.join(root, dir_name)
                    if os.path.exists(full_path):
                        return full_path
    
    # Fallback to regular Desktop
    desktop = os.path.join(home, "Desktop")
    if os.path.exists(desktop):
        return desktop
        
    # Last resort: current directory
    return os.getcwd()

class EnneadKnowledgeBase:
    def __init__(self):
        # Initialize paths
        self.temp_dir = _Exe_Util.WINDOW_TEMP_FOLDER
        self.chat_log_path = os.path.join(self.temp_dir, "EnneaDuck", "chat_logs")
        self.content_path = os.path.join(self.temp_dir, "EnneaDuck", "content.json")
        os.makedirs(os.path.join(self.temp_dir, "EnneaDuck"), exist_ok=True)
        os.makedirs(self.chat_log_path, exist_ok=True)
        
        # Initialize loggers
        self.setup_logging()
        
        # Initialize other attributes
        self.vector_store = None
        self.api_key = None
        self.client = None
        self.last_update = None
        
    def initialize(self):
        """Initialize the knowledge base."""
        try:
            # Try to load existing content first
            if self.initialize_from_saved():
                logging.info("Successfully loaded existing knowledge base")
                return True
                
            # If no existing content or too old, create new
            logging.info("No recent knowledge base found, creating new...")
            content = self.parse_website()
            if content and self.process_content(content):
                logging.info("Successfully created new knowledge base")
                return True
                
            return False
        except Exception as e:
            logging.error(f"Error initializing knowledge base: {e}")
            return False

    def initialize_from_saved(self):
        """Try to initialize from saved content."""
        try:
            if os.path.exists(self.content_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(self.content_path))
                if datetime.now() - file_time <= timedelta(days=VECTOR_STORE_MAX_AGE_DAYS):
                    with open(self.content_path, "r") as f:
                        data = json.load(f)
                        if self.process_content(data['content']):
                            self.last_update = datetime.fromisoformat(data['last_update'])
                            return True
            return False
        except Exception as e:
            logging.error(f"Error loading saved content: {e}")
            return False

    def setup_logging(self):
        """Setup logging for both system and chat logs."""
        # System logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.temp_dir, "EnneaDuck", "system.log")),
                logging.StreamHandler()
            ]
        )
        
        # Chat logging
        self.chat_logger = logging.getLogger('chat_logger')
        self.chat_logger.setLevel(logging.INFO)
        chat_file = os.path.join(self.chat_log_path, f"chat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        chat_handler = logging.FileHandler(chat_file)
        chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.chat_logger.addHandler(chat_handler)

    def get_openai_api_key(self):
        """Get API key with proper error handling."""
        try:
            self.api_key = _Exe_Util.get_openai_api_key("EnneadTabAPI")
            if not self.api_key:
                messagebox.showerror("API Key Error", 
                                   "No OpenAI API key found. Please provide a valid API key.")
                return False
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            messagebox.showerror("API Key Error", 
                               f"Error getting API key: {str(e)}\nPlease provide a valid API key.")
            return False

    def parse_website(self):
        """Parse the Ennead website and extract content from main page and linked pages."""
        try:
            base_url = "https://ennead.com"
            visited_urls = set()
            content = []
            urls_to_visit = [
                base_url,
                base_url + "/work",
                base_url + "/about",
                base_url + "/news",
                base_url + "/careers",
                base_url + "/contact"
            ]
            total_urls_found = 0
            skipped_urls = set()
            
            def parse_page(url, depth=0):
                """Recursively parse a page and its linked pages."""
                nonlocal total_urls_found
                
                if url in visited_urls or len(visited_urls) >= 1000 or depth > 5:
                    if url not in visited_urls:
                        skipped_urls.add(url)
                    return
                    
                visited_urls.add(url)
                print(f"Parsing page {len(visited_urls)}: {url}")
                
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract text content
                    page_content = []
                    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'span']):
                        text = element.get_text(strip=True)
                        if text and len(text) > 20:  # Only keep substantial content
                            page_content.append(text)
                    
                    if page_content:
                        content.extend(page_content)
                        print(f"  Found {len(page_content)} text elements")
                    
                    # Find and follow links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Skip email, phone, and other non-http links
                        if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                            continue
                            
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = base_url + href
                        elif not href.startswith('http'):
                            href = base_url + '/' + href
                            
                        # Clean the URL
                        href = href.split('#')[0]  # Remove anchors
                        href = href.split('?')[0]  # Remove query parameters
                        href = href.rstrip('/')    # Remove trailing slashes
                        
                        # Only follow links to the same domain
                        if href.startswith(base_url) and href not in visited_urls and href not in skipped_urls:
                            # Skip common non-content URLs
                            skip_patterns = [
                                '/wp-content/',
                                '/wp-admin/',
                                '/wp-includes/',
                                '/feed/',
                                '/tag/',
                                '/category/',
                                '/author/',
                                '/page/',
                                '/search/',
                                '/login/',
                                '/register/',
                                '/wp-login.php',
                                '.pdf',
                                '.jpg',
                                '.png',
                                '.gif',
                                '.zip',
                                '.doc',
                                '.docx'
                            ]
                            
                            if not any(pattern in href.lower() for pattern in skip_patterns):
                                urls_to_visit.append(href)
                                total_urls_found += 1
                                print(f"  Found new URL: {href}")
                            
                except Exception as e:
                    print(f"Error parsing page {url}: {e}")
                    logging.error(f"Error parsing page {url}: {e}")
            
            # Start parsing from the main page
            print("\nStarting website parsing...")
            print("=" * 50)
            
            while urls_to_visit and len(visited_urls) < 1000:
                current_url = urls_to_visit.pop(0)
                parse_page(current_url)
                
                # Print progress
                if len(visited_urls) % 10 == 0:
                    print(f"\nProgress: {len(visited_urls)} pages parsed")
                    print(f"URLs in queue: {len(urls_to_visit)}")
                    print(f"Total URLs found: {total_urls_found}")
                    print(f"Skipped URLs: {len(skipped_urls)}")
                    print("=" * 50)
            
            print("\nParsing Summary:")
            print("=" * 50)
            print(f"Total pages parsed: {len(visited_urls)}")
            print(f"Total URLs found: {total_urls_found}")
            print(f"Skipped URLs: {len(skipped_urls)}")
            print(f"Total text elements: {len(content)}")
            print("=" * 50)
            
            if not content:
                print("No content found in website, using default content...")
                # Default content about Ennead Architects
                content = [
                    "Ennead Architects is a leading architectural firm based in New York City.",
                    "Founded in 1963, Ennead has established itself as a premier design practice.",
                    "The firm is known for its innovative approach to architecture and sustainable design.",
                    "Key Projects:",
                    "- Natural History Museum of Utah",
                    "- Yale University's Schwarzman Center",
                    "- Rose Center for Earth and Space at the American Museum of Natural History",
                    "- William J. Clinton Presidential Center",
                    "- The Standard High Line Hotel",
                    "Design Philosophy:",
                    "Ennead's design philosophy emphasizes:",
                    "- Contextual sensitivity",
                    "- Sustainable practices",
                    "- Innovation in form and function",
                    "- Integration of art and architecture",
                    "- Public engagement",
                    "Services Offered:",
                    "- Architectural Design",
                    "- Master Planning",
                    "- Interior Design",
                    "- Sustainable Design",
                    "- Historic Preservation",
                    "- Exhibition Design",
                    "Sustainability:",
                    "Ennead is committed to sustainable design practices, including:",
                    "- LEED certification",
                    "- Energy efficiency",
                    "- Environmental responsibility",
                    "- Green building materials",
                    "Contact Information:",
                    "Ennead Architects",
                    "200 West 57th Street",
                    "New York, NY 10019",
                    "Phone: (212) 629-7262",
                    "Email: info@ennead.com",
                    "Notable Achievements:",
                    "- Multiple AIA Honor Awards",
                    "- National Design Awards",
                    "- Sustainable Design Recognition",
                    "- Historic Preservation Awards",
                    "The firm's work spans various sectors including:",
                    "- Cultural Institutions",
                    "- Educational Facilities",
                    "- Healthcare Buildings",
                    "- Commercial Projects",
                    "- Residential Developments",
                    "Ennead's approach combines:",
                    "- Technical expertise",
                    "- Artistic vision",
                    "- Environmental consciousness",
                    "- Client collaboration"
                ]
            
            return "\n".join(content)
            
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
            return False
            
        try:
            # Get API key before processing
            if not self.get_openai_api_key():
                return False
                
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(content)
            
            # Create embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            
            # Create vector store
            self.vector_store = FAISS.from_texts(chunks, embedding=embeddings)
            
            # Save the content for future use
            store_data = {
                'content': content,
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.content_path, "w") as f:
                json.dump(store_data, f)
                
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            logging.error(f"Error processing content: {e}")
            return False

    def update_knowledge_base(self, new_content):
        """Update the vector store with new content."""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            new_chunks = text_splitter.split_text(new_content)
            
            # Create embeddings for new content
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            
            # If vector store exists, add to it, otherwise create new
            if self.vector_store:
                self.vector_store.add_texts(new_chunks)
            else:
                self.vector_store = FAISS.from_texts(new_chunks, embedding=embeddings)
                
            return True
        except Exception as e:
            logging.error(f"Error updating knowledge base: {e}")
            return False

    def get_response(self, query):
        """Get response for user query using vector store and GPT-4."""
        if not self.vector_store:
            return "Knowledge base not initialized. Please click 'Update Knowledge' to initialize."
            
        try:
            # Log the user query
            self.chat_logger.info(f"User: {query}")
            
            # Get relevant documents
            docs = self.vector_store.similarity_search(query, k=5)
            context = ' '.join([doc.page_content for doc in docs])
            
            # Check if the context seems insufficient
            system_prompt = """You are EnneaDuck, a helpful assistant for Ennead Architects users. 
            Analyze if the provided context is sufficient to answer the user's question.
            If the context doesn't contain relevant information, respond with 'INSUFFICIENT_CONTEXT'.
            Otherwise, provide a clear, concise answer based on the context."""
            
            check_response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            initial_assessment = check_response.choices[0].message.content
            
            if "INSUFFICIENT_CONTEXT" in initial_assessment:
                return "Sorry, I cannot find the answer in my current knowledge base. I'll search for more information and update my knowledge base. Please click the 'Update Knowledge' button to refresh my knowledge with additional content."
            
            # Get final response
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are EnneaDuck, a helpful assistant for Ennead Architects users. Provide clear, concise answers based on the context provided."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Log the response
            self.chat_logger.info(f"EnneaDuck: {answer}")
            
            return answer
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.chat_logger.error(error_msg)
            return error_msg

class ModernChatUI:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.username = getpass.getuser()
        self.setup_ui()
        
        # Initialize knowledge base after UI setup
        self.initialize_knowledge_base()
        
    def setup_ui(self):
        """Create modern game-like chat interface."""
        self.root = tk.Tk()
        self.root.title("EnneaDuck - Ennead Intelligence Hub")
        self.root.geometry("1000x700")
        
        # Custom colors
        self.colors = {
            'bg_dark': '#1E1E1E',
            'bg_light': '#2D2D2D',
            'accent': '#007ACC',
            'text': '#E0E0E0',
            'text_dim': '#A0A0A0',
            'success': '#4CAF50',
            'error': '#F44336',
            'user_bubble': '#3A3F4B',  # New color for user bubbles
            'assistant_bubble': '#23272E'  # New color for assistant bubbles
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Custom styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Chat.TFrame', background=self.colors['bg_dark'])
        style.configure('Header.TLabel', 
                       background=self.colors['bg_dark'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Status.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_dim'],
                       font=('Segoe UI', 9))
        style.configure('Timestamp.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_dim'],
                       font=('Segoe UI', 8))
        style.configure('Custom.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       padding=10)
        
        # Create main container
        main_container = ttk.Frame(self.root, style='Chat.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container, style='Chat.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, 
                               text="EnneaDuck - Ennead Intelligence Hub",
                               style='Header.TLabel')
        header_label.pack(side=tk.LEFT)
        
        # Update button
        self.update_button = tk.Button(
            header_frame,
            text="Update Knowledge",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['bg_light'],
            activeforeground=self.colors['text'],
            relief=tk.FLAT,
            command=self.update_knowledge,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.update_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Status frame
        self.status_frame = ttk.Frame(header_frame, style='Chat.TFrame')
        self.status_frame.pack(side=tk.RIGHT)
        
        # Status indicator
        self.status_indicator = tk.Canvas(self.status_frame, 
                                        width=10, height=10,
                                        bg=self.colors['bg_dark'],
                                        highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self.status_indicator.create_oval(2, 2, 8, 8, 
                                        fill=self.colors['success'],
                                        tags='status')
        
        # Status label
        self.status_label = ttk.Label(self.status_frame,
                                    text="Ready",
                                    style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        # Timestamp label
        self.timestamp_label = ttk.Label(self.status_frame,
                                       text="Last updated: Never",
                                       style='Timestamp.TLabel')
        self.timestamp_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update timestamp
        self.update_timestamp()
        
        # Chat display
        self.chat_frame = ttk.Frame(main_container, style='Chat.TFrame')
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbar for the chat
        self.chat_canvas = tk.Canvas(
            self.chat_frame,
            bg=self.colors['bg_light'],
            highlightthickness=0
        )
        self.chat_scrollbar = ttk.Scrollbar(
            self.chat_frame,
            orient="vertical",
            command=self.chat_canvas.yview
        )
        
        # Create a frame inside the canvas for messages
        self.message_frame = ttk.Frame(self.chat_canvas, style='Chat.TFrame')
        self.message_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the message frame
        self.chat_canvas.create_window((0, 0), window=self.message_frame, anchor="nw", width=self.chat_canvas.winfo_reqwidth())
        
        # Configure canvas scrolling
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse wheel to scroll
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Input area
        input_frame = ttk.Frame(main_container, style='Chat.TFrame')
        input_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.message_input = tk.Text(
            input_frame,
            height=3,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind('<Return>', self.handle_return)
        self.message_input.bind('<Shift-Return>', self.handle_shift_return)
        
        # Send button with gaming style
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['bg_light'],
            activeforeground=self.colors['text'],
            relief=tk.FLAT,
            command=self.send_message,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Add welcome message and suggested topics
        self.add_system_message(f"Welcome {self.username}! I'm EnneaDuck, your Ennead Architects assistant.")
        self.add_system_message("Here are some topics you might want to ask about:")
        for topic in SUGGESTED_TOPICS:
            self.add_system_message(f"• {topic}")
        
    def update_timestamp(self):
        """Update the timestamp label with last update time."""
        if self.kb.last_update:
            timestamp = self.kb.last_update.strftime("%Y-%m-%d %H:%M:%S")
            self.timestamp_label.configure(text=f"Last updated: {timestamp}")
        else:
            self.timestamp_label.configure(text="Last updated: Never")
            
    def initialize_knowledge_base(self):
        """Initialize the knowledge base on startup."""
        self.set_status("Initializing...")
        self.update_button.configure(state='disabled')
        
        def init():
            try:
                if self.kb.initialize():
                    self.root.after(0, lambda: self.add_system_message("Knowledge base loaded successfully!"))
                    self.root.after(0, self.update_timestamp)
                else:
                    self.root.after(0, lambda: self.add_system_message("Please click 'Update Knowledge' to initialize the knowledge base."))
            except Exception as e:
                self.root.after(0, lambda: self.add_system_message(f"Error initializing knowledge base: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.update_button.configure(state='normal'))
                self.root.after(0, lambda: self.set_status("Ready"))
        
        threading.Thread(target=init, daemon=True).start()

    def update_knowledge(self):
        """Update the knowledge base."""
        self.update_button.configure(state='disabled')
        self.set_status("Updating knowledge base...")
        
        def update():
            try:
                if not self.kb.get_openai_api_key():
                    self.root.after(0, lambda: self.update_button.configure(state='normal'))
                    return
                    
                content = self.kb.parse_website()
                if content and self.kb.process_content(content):
                    self.root.after(0, lambda: self.add_system_message("Knowledge base updated successfully!"))
                    self.root.after(0, self.update_timestamp)
                else:
                    self.root.after(0, lambda: self.add_system_message("Failed to update knowledge base."))
            except Exception as e:
                self.root.after(0, lambda: self.add_system_message(f"Error updating knowledge base: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.update_button.configure(state='normal'))
                self.root.after(0, lambda: self.set_status("Ready"))
        
        threading.Thread(target=update, daemon=True).start()

    def handle_return(self, event):
        """Handle Return key press."""
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return 'break'
        return None
        
    def handle_shift_return(self, event):
        """Handle Shift+Return key press."""
        return None  # Allow default behavior (new line)
        
    def set_status(self, status, is_error=False):
        """Update status indicator and label."""
        color = self.colors['error'] if is_error else self.colors['success']
        self.status_indicator.itemconfig('status', fill=color)
        self.status_label.configure(text=status)
        
    def add_system_message(self, message):
        """Add a system message to the chat."""
        message_frame = ttk.Frame(self.message_frame, style='Chat.TFrame')
        message_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Create message bubble
        bubble = tk.Frame(
            message_frame,
            bg=self.colors['bg_light'],
            highlightbackground=self.colors['accent'],
            highlightthickness=1,
            padx=15,
            pady=10
        )
        bubble.pack(fill=tk.X, anchor='w', expand=True)
        
        # Add message text
        label = tk.Label(
            bubble,
            text=message,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['accent'],
            wraplength=700,
            justify=tk.LEFT,
            anchor='w'
        )
        label.pack(fill=tk.X, anchor='w', expand=True)
        
        # Scroll to bottom
        self.chat_canvas.yview_moveto(1.0)
        
    def add_message(self, sender, message):
        """Add a message to the chat display with styling."""
        message_frame = ttk.Frame(self.message_frame, style='Chat.TFrame')
        message_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Create header with timestamp and sender
        header_frame = ttk.Frame(message_frame, style='Chat.TFrame')
        header_frame.pack(fill=tk.X)
        
        timestamp = datetime.now().strftime("%H:%M")
        timestamp_label = ttk.Label(
            header_frame,
            text=timestamp,
            style='Timestamp.TLabel'
        )
        timestamp_label.pack(side=tk.LEFT)
        
        sender_label = ttk.Label(
            header_frame,
            text=sender,
            style='Header.TLabel' if sender == "Assistant" else 'Status.TLabel'
        )
        sender_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Determine alignment and bubble color
        if sender == "Assistant":
            bubble_bg = self.colors['assistant_bubble']
            bubble_fg = self.colors['text']
            bubble_side = tk.LEFT
            anchor = 'w'
        else:
            bubble_bg = self.colors['user_bubble']
            bubble_fg = self.colors['text']
            bubble_side = tk.RIGHT
            anchor = 'e'
        
        # Create message bubble
        bubble = tk.Frame(
            message_frame,
            bg=bubble_bg,
            highlightbackground=self.colors['accent'] if sender == "Assistant" else self.colors['success'],
            highlightthickness=1,
            padx=15,
            pady=10
        )
        bubble.pack(fill=tk.NONE, side=bubble_side, anchor=anchor, expand=False)
        
        # Add message text
        label = tk.Label(
            bubble,
            text=message,
            font=('Segoe UI', 11),
            bg=bubble_bg,
            fg=bubble_fg,
            wraplength=700,
            justify=tk.LEFT,
            anchor='w'
        )
        label.pack(fill=tk.BOTH, anchor='w', expand=True)
        
        # Scroll to bottom
        self.chat_canvas.yview_moveto(1.0)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def send_message(self):
        """Handle sending messages with animation."""
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
            
        # Clear input and disable
        self.message_input.delete("1.0", tk.END)
        self.message_input.configure(state='disabled')
        self.send_button.configure(state='disabled')
        
        # Update status
        self.set_status("Thinking...")
        
        # Add user message
        self.add_message("You", message)
        
        # Get response in a separate thread
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
        
    def get_ai_response(self, message):
        """Get AI response in a separate thread."""
        try:
            response = self.kb.get_response(message)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.add_message("Assistant", response))
            self.root.after(0, lambda: self.set_status("Ready"))
            self.root.after(0, lambda: self.message_input.configure(state='normal'))
            self.root.after(0, lambda: self.send_button.configure(state='normal'))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.add_system_message(error_msg))
            self.root.after(0, lambda: self.set_status("Error occurred", True))
            self.root.after(0, lambda: self.message_input.configure(state='normal'))
            self.root.after(0, lambda: self.send_button.configure(state='normal'))
            
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()

def main():
    try:
        # Initialize knowledge base
        kb = EnneadKnowledgeBase()
        
        # Start UI
        ui = ModernChatUI(kb)
        ui.run()
        
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
