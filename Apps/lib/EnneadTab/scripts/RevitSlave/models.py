"""
Models for RevitSlave application.

This module contains the core data models for Revit projects and models.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class RevitModel:
    """
    Represents a Revit model with its metadata.

    This class is your backstage pass to all the juicy details about a Revit model!
    """
    model_guid: str
    project_guid: str
    revit_version: str
    region: str
    name: str = ""
    last_modified: str = ""
    path: str = ""

    @classmethod
    def from_data_dict(cls, name: str, data: Dict) -> 'RevitModel':
        """
        Create a RevitModel instance from a data dictionary as found in the data file.
        Args:
            name (str): The name/key of the model in the data file.
            data (dict): The model data dictionary.
        Returns:
            RevitModel: The constructed model instance.
        """
        return cls(
            model_guid=data["model_guid"],
            project_guid=data["project_guid"],
            revit_version=data["revit_version"],
            region=data.get("region", ""),
            name=name
        )
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RevitModel':
        """Create a RevitModel instance from a dictionary."""
        return cls(
            model_guid=data['model_guid'],
            project_guid=data['project_guid'],
            revit_version=data['revit_version'],
            region=data.get('region', ''),
            name=data['name'],
            last_modified=data['last_modified'],
            path=data['path']
        )
    
    def to_dict(self) -> Dict:
        """Convert the model to a dictionary."""
        return {
            'model_guid': self.model_guid,
            'project_guid': self.project_guid,
            'revit_version': self.revit_version,
            'region': self.region,
            'name': self.name,
            'last_modified': self.last_modified,
            'path': self.path
        }


@dataclass
class RevitProject:
    """Represents a Revit project with its associated models."""
    
    guid: str
    name: str
    models: List[RevitModel]
    last_updated: datetime
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RevitProject':
        """Create a RevitProject instance from a dictionary."""
        return cls(
            guid=data['guid'],
            name=data['name'],
            models=[RevitModel.from_dict(model_data) for model_data in data['models']],
            last_updated=datetime.fromisoformat(data['last_updated'])
        )
    
    def to_dict(self) -> Dict:
        """Convert the project to a dictionary."""
        return {
            'guid': self.guid,
            'name': self.name,
            'models': [model.to_dict() for model in self.models],
            'last_updated': self.last_updated.isoformat()
        }
    
    def get_model_by_guid(self, guid: str) -> Optional[RevitModel]:
        """Get a model by its GUID."""
        return next((model for model in self.models if model.model_guid == guid), None) 