"""
Data models and structures for EnneadTabAgent

This module defines the key data structures used throughout the application
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import json

@dataclass
class Message:
    """Chat message model."""
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API calls."""
        return {
            "role": self.role,
            "content": self.content
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Message':
        """Create from JSON dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp
        )


@dataclass
class Conversation:
    """Chat conversation model."""
    messages: List[Message] = field(default_factory=list)
    id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    title: str = "New Conversation"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str) -> Message:
        """Add a message to the conversation."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_api_messages(self) -> List[Dict[str, str]]:
        """Convert messages to format for API calls."""
        return [msg.to_dict() for msg in self.messages]
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_json() for msg in self.messages]
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create from JSON dictionary."""
        messages = [Message.from_json(msg) for msg in data.get("messages", [])]
        return cls(
            messages=messages,
            id=data.get("id", datetime.now().strftime("%Y%m%d_%H%M%S")),
            title=data.get("title", "Imported Conversation"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
    
    def save_to_file(self, filepath: str) -> bool:
        """Save conversation to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_json(), f, indent=2)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['Conversation']:
        """Load conversation from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls.from_json(data)
        except Exception:
            return None


@dataclass
class SearchResult:
    """Search result from vector store."""
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    
    @property
    def source(self) -> str:
        """Get source of the document."""
        return self.metadata.get("source", "Unknown")
    
    @property
    def url(self) -> str:
        """Get URL of the document."""
        return self.metadata.get("url", "")
    
    @property
    def title(self) -> str:
        """Get title of the document."""
        return self.metadata.get("title", "Untitled")


@dataclass
class ContentItem:
    """Content item from web scraping."""
    url: str
    title: str
    text: str
    source: str = "Ennead Website"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create from dictionary."""
        return cls(
            url=data["url"],
            title=data["title"],
            text=data["text"],
            source=data.get("source", "Ennead Website"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )


@dataclass
class KnowledgeBaseStats:
    """Statistics about the knowledge base."""
    document_count: int = 0
    source_count: int = 0
    sources: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    crawl_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_count": self.document_count,
            "source_count": self.source_count,
            "sources": self.sources,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "crawl_details": self.crawl_details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeBaseStats':
        """Create from dictionary."""
        last_updated = None
        if data.get("last_updated"):
            try:
                last_updated = datetime.fromisoformat(data["last_updated"])
            except (ValueError, TypeError):
                pass
                
        return cls(
            document_count=data.get("document_count", 0),
            source_count=data.get("source_count", 0),
            sources=data.get("sources", []),
            last_updated=last_updated,
            crawl_details=data.get("crawl_details", {})
        ) 