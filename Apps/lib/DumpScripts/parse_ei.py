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
from datetime import datetime
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
        self.vector_store_path = os.path.join(find_onedrive_desktop(), "ennead_knowledge.pkl")
        self.vector_store = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("ennead_kb.log"),
                logging.StreamHandler()
            ]
        )
        
    def parse_website(self):
        """Parse the Ennead website and extract content from main page and linked pages."""
        try:
            base_url = "https://ei.ennead.com"
            visited_urls = set()
            content = []
            
            def parse_page(url):
                """Recursively parse a page and its linked pages."""
                if url in visited_urls or len(visited_urls) > 50:  # Limit to 50 pages to avoid infinite loops
                    return
                    
                visited_urls.add(url)
                print(f"Parsing page: {url}")
                
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract text content
                    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                        text = element.get_text(strip=True)
                        if text:
                            content.append(text)
                    
                    # Find and follow links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = base_url + href
                        # Only follow links to the same domain
                        if href.startswith(base_url):
                            parse_page(href)
                            
                except Exception as e:
                    print(f"Error parsing page {url}: {e}")
                    logging.error(f"Error parsing page {url}: {e}")
            
            # Start parsing from the main page
            print("Starting website parsing...")
            parse_page(base_url)
            
            if not content:
                print("No content found in website, using sample content for testing...")
                # Sample content about Ennead Tab
                content = [
                    "Welcome to Ennead Tab",
                    "Ennead Tab is a powerful suite of tools for architects and designers.",
                    "Key Features:",
                    "- Automated drawing and modeling tools",
                    "- Project management utilities",
                    "- Custom Revit and Rhino extensions",
                    "- AI-powered assistance",
                    "- Collaboration tools",
                    "Usage:",
                    "1. Install Ennead Tab through the installer",
                    "2. Access tools through the Ennead Tab ribbon",
                    "3. Use the AI assistant for help and questions",
                    "4. Check documentation for detailed instructions",
                    "Benefits:",
                    "- Increased productivity",
                    "- Standardized workflows",
                    "- Reduced manual work",
                    "- Better collaboration",
                    "For support or questions, contact the Ennead Tab team."
                ]
            
            print(f"Successfully extracted {len(content)} text elements from {len(visited_urls)} pages")
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
            return
            
        # Get API key before processing
        self.api_key = _Exe_Util.get_api_key("EnneadTabAPI")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
            
        self.client = OpenAI(api_key=self.api_key)
            
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
        
        # Save vector store
        with open(self.vector_store_path, "wb") as f:
            pickle.dump(self.vector_store, f)
            
    def load_vector_store(self):
        """Load existing vector store if available."""
        if os.path.exists(self.vector_store_path):
            with open(self.vector_store_path, "rb") as f:
                self.vector_store = pickle.load(f)
            return True
        return False
        
    def get_response(self, query):
        """Get response for user query using vector store and GPT-4."""
        if not self.vector_store:
            return "Knowledge base not initialized. Please parse the website first."
            
        # Get API key if not already set
        if not hasattr(self, 'api_key'):
            self.api_key = _Exe_Util.get_api_key("EnneadTabAPI")
            if not self.api_key:
                return "Error: OpenAI API key not found"
            self.client = OpenAI(api_key=self.api_key)
            
        # Get relevant documents
        docs = self.vector_store.similarity_search(query, k=5)
        
        # Create prompt
        prompt = f"""Based on the following context from the Ennead website, answer the question.
        If the answer cannot be found in the context, say so.
        
        Context:
        {' '.join([doc.page_content for doc in docs])}
        
        Question: {query}
        
        Answer:"""
        
        # Get response from GPT-4
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Ennead Tab users. Provide clear, concise answers based on the context provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

class ModernChatUI:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.setup_ui()
        
    def setup_ui(self):
        """Create modern game-like chat interface."""
        self.root = tk.Tk()
        self.root.title("Ennead Knowledge Chat")
        self.root.geometry("800x600")
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = "#2C2F33"
        text_color = "#FFFFFF"
        accent_color = "#7289DA"
        
        self.root.configure(bg=bg_color)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            bg=bg_color,
            fg=text_color,
            font=("Segoe UI", 10),
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # Message input
        self.message_input = ttk.Entry(
            input_frame,
            font=("Segoe UI", 10)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", self.send_message)
        
        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 8)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Add welcome message
        self.add_message("System", "Welcome to Ennead Knowledge Chat! Type your questions about Ennead Tab here.")
        
    def add_message(self, sender, message):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        
    def send_message(self, event=None):
        """Handle sending messages."""
        message = self.message_input.get().strip()
        if not message:
            return
            
        self.message_input.delete(0, tk.END)
        self.add_message("You", message)
        
        # Update status
        self.status_var.set("Thinking...")
        self.root.update()
        
        # Get response in a separate thread
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
        
    def get_ai_response(self, message):
        """Get AI response in a separate thread."""
        try:
            response = self.kb.get_response(message)
            self.root.after(0, lambda: self.add_message("Assistant", response))
            self.root.after(0, lambda: self.status_var.set("Ready"))
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.add_message("System", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
            
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()

def setup_test_api_key():
    """Create a temporary API key file for testing."""
    # Get the API key from environment variable or ask user
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nNo OpenAI API key found in environment variables.")
        print("Please enter your OpenAI API key (or press Enter to exit):")
        api_key = input().strip()
        if not api_key:
            sys.exit(1)
    
    # Create temporary API key file
    dump_folder = os.path.join(os.path.expanduser("~"), "Documents", "EnneadTab-Ecosystem", "Dump")
    os.makedirs(dump_folder, exist_ok=True)
    
    api_key_data = {"EnneadTabAPI": api_key}
    api_key_file = os.path.join(dump_folder, "EA_API_KEY.secret")
    
    with open(api_key_file, "w") as f:
        json.dump(api_key_data, f)
    
    return api_key_file

def main():
    try:
        # Setup test API key
        api_key_file = setup_test_api_key()
        print(f"Using API key file: {api_key_file}")
        
        # Initialize knowledge base
        kb = EnneadKnowledgeBase()
        
        # Load or create vector store
        if not kb.load_vector_store():
            print("Parsing website and creating knowledge base...")
            content = kb.parse_website()
            if content:
                kb.process_content(content)
                print("Knowledge base created successfully!")
            else:
                print("Failed to parse website content.")
                return
                
        # Start UI
        ui = ModernChatUI(kb)
        ui.run()
        
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
