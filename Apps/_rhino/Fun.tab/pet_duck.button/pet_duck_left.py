__title__ = "PetDuck"
__doc__ = """
DuckiTect - Professional Architecture Assistant
--------------------------------------------

A sophisticated desktop companion integrating architectural expertise with advanced AI capabilities.

Core Features:
- Intelligent Interaction:
    * Natural language processing
    * Advanced GPT integration
    * Professional formatting
    * Context-aware responses

- Architecture Tools:
    * Building code library
    * Design research portal
    * Documentation helper
    * Drawing analysis

- Professional Tools:
    * Rhino/Grasshopper tools
    * BIM workflow aids
    * Error tracking system
    * Markdown support

Usage:
Left click to activate DuckiTect
"""

from EnneadTab import ERROR_HANDLE, LOG, JOKE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def pet_duck():
    """
    Initialize DuckiTect assistant.
    
    Components:
    - AI chat system
    - Workspace tools
    - Error handling
    - Session manager
    """
    JOKE.ennead_duck()
    
if __name__ == "__main__":
    pet_duck()
