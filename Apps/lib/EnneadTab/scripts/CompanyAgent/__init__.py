"""
EnneadTabAgent - An AI assistant integrated with Ennead Architects knowledge

Structure:
----------

__init__.py
- Entry point of the app
- Central initialization and API exports

vector_store.py
- Handle vector database operations (FAISS)
- Document chunking and embedding
- Knowledge retrieval and search

content_manager.py
- Web scraping and content collection
- Content processing and normalization
- Knowledge base updating and maintenance

ui.py
- Modern chat interface with tkinter
- Message history and conversation tracking
- Suggested queries and interactive elements

utils.py
- API key management
- File system operations
- Logging and error handling
- Integration with other EnneadTab modules

constants.py
- Configuration settings
- UI elements and styling
- System prompts and templates

models.py
- Data models and structures
- Type definitions
- Schema validation

Key Features:
-------------
- Semantic search of Ennead knowledge
- Attractive, user-friendly chat interface
- Regular knowledge base updates
- Persistent conversation history
- Integration with existing EnneadTab ecosystem


"""

# Import version and metadata
__version__ = "0.1.0"
__author__ = "Ennead Architects"

# Import main classes for easy access
from .__main__ import EnneadTabAgent, main

def run():
    """Convenience function to run the application."""
    main()

# Allow direct execution of the module
if __name__ == "__main__":
    run()