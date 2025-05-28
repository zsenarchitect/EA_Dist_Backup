"""
Version control module for RevitSlave.

This module handles version tracking and management for Revit models.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from .models import RevitModel, RevitProject


class VersionControl:
    """Manages version control for Revit models."""
    
    def __init__(self, data_file: Path):
        """Initialize version control with data file path."""
        self.data_file = data_file
        self._projects: Dict[str, RevitProject] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load version data from file."""
        if not self.data_file.exists():
            return
            
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, dict):
            for project_data in data.values():
                project = RevitProject.from_dict(project_data)
                self._projects[project.guid] = project
    
    def _save_data(self) -> None:
        """Save version data to file."""
        data = {project.guid: project.to_dict() for project in self._projects.values()}
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_project(self, guid: str) -> Optional[RevitProject]:
        """Get a project by its GUID."""
        return self._projects.get(guid)
    
    def get_model(self, project_guid: str, model_guid: str) -> Optional[RevitModel]:
        """Get a model by project and model GUIDs."""
        project = self.get_project(project_guid)
        return project.get_model_by_guid(model_guid) if project else None
    
    def update_model(self, model: RevitModel) -> None:
        """Update model information."""
        project = self._projects.get(model.project_guid)
        if not project:
            return
            
        existing_model = project.get_model_by_guid(model.guid)
        if existing_model:
            project.models.remove(existing_model)
        project.models.append(model)
        project.last_updated = datetime.now()
        self._save_data()
    
    def add_project(self, project: RevitProject) -> None:
        """Add a new project."""
        self._projects[project.guid] = project
        self._save_data() 