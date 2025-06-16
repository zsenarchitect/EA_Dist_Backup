"""
Vector store management for EnneadTabAgent

This module handles:
- Creating and updating the FAISS vector store
- Text chunking and embedding
- Vector search functionality
"""

import os
import sys
import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path

# For vector database
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Import local modules
from . import utils
from . import constants

class VectorStore:
    def __init__(self):
        """Initialize the vector store component."""
        self.logger = logging.getLogger("EnneadTabAgent.vector_store")
        self.vector_store = None
        self.vector_store_path = utils.get_storage_path("ennead_knowledge.pkl")
        self.metadata_path = utils.get_storage_path("ennead_knowledge_stats.json")
        self.embeddings = None
        self.last_updated = None
        
    def initialize(self):
        """Initialize or load the vector store."""
        try:
            # Try to load existing vector store
            if self.load_vector_store():
                self.logger.info("Successfully loaded existing vector store")
                return True
                
            # If no vector store exists, we'll need content to create one
            self.logger.info("No vector store found, one will need to be created with content")
            return False
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {e}")
            return False

    def load_vector_store(self):
        """Load the vector store from disk if it exists and is not too old."""
        try:
            if not os.path.exists(self.vector_store_path):
                self.logger.info(f"Vector store file not found at {self.vector_store_path}")
                return False
                
            # Check age of vector store
            file_time = datetime.fromtimestamp(os.path.getmtime(self.vector_store_path))
            max_age = constants.VECTOR_STORE_MAX_AGE_DAYS
            
            if datetime.now() - file_time > timedelta(days=max_age):
                self.logger.info(f"Vector store is older than {max_age} days, will create a new one")
                return False
                
            # Load vector store with proper API key
            if not self.initialize_embeddings():
                return False
                
            with open(self.vector_store_path, "rb") as f:
                self.vector_store = pickle.load(f)
                
            # Load metadata
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r") as f:
                    metadata = json.load(f)
                    if "last_updated" in metadata:
                        self.last_updated = datetime.fromisoformat(metadata["last_updated"])
                        
            self.logger.info(f"Successfully loaded vector store from {self.vector_store_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading vector store: {e}")
            return False
            
    def initialize_embeddings(self):
        """Initialize the OpenAI embeddings with API key."""
        try:
            api_key = utils.get_openai_api_key()
            if not api_key:
                self.logger.error("Failed to get API key for embeddings")
                return False
                
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            return True
        except Exception as e:
            self.logger.error(f"Error initializing embeddings: {e}")
            return False
            
    def create_vector_store(self, documents):
        """Create a new vector store from documents."""
        try:
            if not self.initialize_embeddings():
                return False
                
            # Create new vector store
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # Save to disk
            self.save_vector_store()
            return True
        except Exception as e:
            self.logger.error(f"Error creating vector store: {e}")
            return False
            
    def update_vector_store(self, new_documents):
        """Update existing vector store with new documents."""
        try:
            if not self.vector_store:
                return self.create_vector_store(new_documents)
                
            # Add new documents to existing vector store
            if new_documents:
                self.vector_store.add_documents(new_documents)
                
            # Save to disk
            self.save_vector_store()
            return True
        except Exception as e:
            self.logger.error(f"Error updating vector store: {e}")
            return False
            
    def save_vector_store(self):
        """Save vector store to disk with metadata."""
        try:
            # Save vector store
            with open(self.vector_store_path, "wb") as f:
                pickle.dump(self.vector_store, f)
                
            # Update and save metadata
            self.last_updated = datetime.now()
            metadata = {
                "last_updated": self.last_updated.isoformat(),
                "document_count": len(self.vector_store.index_to_docstore_id) if self.vector_store else 0
            }
            
            with open(self.metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            self.logger.info(f"Successfully saved vector store to {self.vector_store_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving vector store: {e}")
            return False
            
    def search(self, query, k=4):
        """Search the vector store for documents relevant to query."""
        try:
            if not self.vector_store:
                self.logger.error("No vector store available for search")
                return []
                
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            self.logger.error(f"Error searching vector store: {e}")
            return []
            
    def process_text(self, texts, metadatas=None):
        """Process text into chunks suitable for the vector store."""
        try:
            # Setup text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=constants.CHUNK_SIZE,
                chunk_overlap=constants.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            
            # Split texts into chunks
            if metadatas:
                documents = text_splitter.create_documents(texts, metadatas=metadatas)
            else:
                documents = text_splitter.create_documents(texts)
                
            return documents
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            return []
            
    def get_stats(self):
        """Get statistics about the vector store."""
        stats = {
            "last_updated": self.last_updated.isoformat() if self.last_updated else "Never",
            "document_count": 0,
            "source_count": 0,
            "sources": []
        }
        
        if not self.vector_store:
            return stats
            
        try:
            # Get document count
            stats["document_count"] = len(self.vector_store.index_to_docstore_id)
            
            # Extract source information
            sources = set()
            for doc_id in self.vector_store.index_to_docstore_id.values():
                doc = self.vector_store.docstore.search(doc_id)
                if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.add(doc.metadata['source'])
                elif hasattr(doc, 'metadata') and 'url' in doc.metadata:
                    sources.add(doc.metadata['url'])
                    
            stats["source_count"] = len(sources)
            stats["sources"] = list(sources)[:10]  # Limit to 10 sources
        except Exception as e:
            self.logger.error(f"Error getting vector store stats: {e}")
            
        return stats 