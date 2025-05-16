"""
Main entry point for EnneadTabAgent

This module initializes and runs the EnneadTabAgent application
"""

import os
import sys
import logging
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI

# Import local modules
from . import constants
from . import utils
from . import vector_store
from . import content_manager
from . import models
from . import ui

class EnneadTabAgent:
    """Main agent class that coordinates all components."""
    
    def __init__(self):
        """Initialize the agent."""
        # Setup logging
        utils.setup_logging()
        self.logger = logging.getLogger("EnneadTabAgent")
        self.logger.info("Initializing EnneadTabAgent")
        
        # Initialize components
        self.vector_store = vector_store.VectorStore()
        self.content_manager = content_manager.ContentManager(self.vector_store)
        self.client = None
        self.ui = None
        self.current_conversation = models.Conversation()
        
    def initialize(self):
        """Initialize all components of the agent."""
        try:
            # Initialize OpenAI client
            api_key = utils.get_api_key()
            if not api_key:
                self.logger.error("No API key found, cannot continue")
                return False
                
            self.client = OpenAI(api_key=api_key)
            
            # Initialize vector store
            vector_store_initialized = self.vector_store.initialize()
            if not vector_store_initialized:
                self.logger.warning("Vector store not initialized, will create on first content update")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing agent: {e}")
            return False
            
    def get_response(self, query):
        """Get a response to a user query."""
        try:
            self.logger.info(f"Processing query: {query}")
            
            # Search vector store for relevant context
            results = self.vector_store.search(query, k=4)
            
            if not results:
                self.logger.warning("No relevant information found in knowledge base")
                # Fallback to general query
                return self.generate_response(query)
                
            # Format context from search results
            context = "\n\n".join([doc.page_content for doc in results])
            
            # Generate response with context
            return self.generate_response(query, context)
            
        except Exception as e:
            self.logger.error(f"Error getting response: {e}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"
            
    def generate_response(self, query, context=None):
        """Generate a response using OpenAI's API."""
        try:
            messages = []
            
            # System message with instructions
            system_message = constants.SYSTEM_PROMPT
            if context:
                system_message += "\n\nUse the following information to answer the user's question:\n" + context
                
            messages.append({"role": "system", "content": system_message})
            
            # Add conversation history (limited to last 10 messages)
            history = self.current_conversation.messages[-10:]
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
                
            # Add the current query
            messages.append({"role": "user", "content": query})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=constants.MODEL_NAME,
                messages=messages,
                temperature=constants.TEMPERATURE,
                max_tokens=constants.MAX_TOKENS
            )
            
            # Extract and return the response
            reply = response.choices[0].message.content
            
            # Update conversation history
            self.current_conversation.add_message("user", query)
            self.current_conversation.add_message("assistant", reply)
            
            return reply
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
            
    def update_knowledge_base(self, force_update=False):
        """Update the knowledge base."""
        try:
            return self.content_manager.update_knowledge_base(force_update)
        except Exception as e:
            self.logger.error(f"Error updating knowledge base: {e}")
            return False
            
    def update_knowledge_base_async(self, callback=None, force_update=False):
        """Update knowledge base in a background thread."""
        return self.content_manager.update_knowledge_base_async(callback, force_update)
        
    def run(self):
        """Run the agent with UI."""
        try:
            # Initialize components
            if not self.initialize():
                messagebox.showerror(
                    "Initialization Error",
                    "Failed to initialize EnneadTabAgent. Check the logs for details."
                )
                return
                
            # Create and run UI
            self.ui = ui.ModernChatUI(self)
            self.ui.run()
            
        except Exception as e:
            self.logger.error(f"Error running agent: {e}")
            messagebox.showerror(
                "Error",
                f"An error occurred while running EnneadTabAgent: {str(e)}"
            )

def main():
    """Main entry point."""
    agent = EnneadTabAgent()
    agent.run()
    
if __name__ == "__main__":
    main() 