"""
Configuration module for RevitSlave.

This module handles application configuration and settings.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass, asdict


@dataclass
class Config:
    """Application configuration settings."""
    
    data_file: Path
    max_workers: int = 4
    log_level: str = "INFO"
    task_interval: int = 3600  # seconds
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from file."""
        if not config_path.exists():
            return cls(data_file=Path("DOC_OPENER_DATA.sexyDuck"))
            
        with open(config_path, 'r') as f:
            data = json.load(f)
            
        return cls(
            data_file=Path(data.get('data_file', "DOC_OPENER_DATA.sexyDuck")),
            max_workers=data.get('max_workers', 4),
            log_level=data.get('log_level', "INFO"),
            task_interval=data.get('task_interval', 3600)
        )
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    def update(self, **kwargs) -> None:
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value) 