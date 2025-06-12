__title__ = "PetDuck"
__doc__ = """
DuckiTect - AI Architecture Assistant
------------------------------------

A desktop companion that combines architectural expertise with AI capabilities.

Features:
- AI-powered chat and analysis
- Architecture tools and code library
- Rhino/Grasshopper integration
- Professional documentation support

Usage: Left click to activate
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
