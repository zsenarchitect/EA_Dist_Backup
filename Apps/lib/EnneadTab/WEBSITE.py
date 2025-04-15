#!python3
"""
This module generates a static documentation website for EnneadTab.
The website includes search functionality and a tree structure navigation sidebar.
Output is generated to the /docs folder in repository root for GitHub Pages compatibility.
"""

import os
import inspect
import json
from pathlib import Path
import shutil
from typing import Dict, List, Any
import re

class DocumentationGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.template_dir = self.base_dir / "documents" / "website"
        self.output_dir = Path(__file__).parent.parent.parent.parent / "Help-Docs"
        self.module_data = {}
        
    def parse_module(self, module_path: Path) -> Dict[str, Any]:
        """Parse a Python module and extract its documentation."""
        module_data = {
            "name": module_path.stem,
            "docstring": "",
            "functions": [],
            "classes": []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract module docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                module_data["docstring"] = docstring_match.group(1).strip()
                
            # Extract functions and their docstrings
            function_matches = re.finditer(r'def\s+(\w+)\s*\((.*?)\):\s*("""(.*?)""")?', content, re.DOTALL)
            for match in function_matches:
                function_data = {
                    "name": match.group(1),
                    "params": match.group(2),
                    "docstring": match.group(4).strip() if match.group(4) else ""
                }
                module_data["functions"].append(function_data)
                
        except Exception as e:
            print(f"Error parsing {module_path}: {str(e)}")
            
        return module_data
    
    def generate_search_index(self) -> List[Dict[str, str]]:
        """Generate search index for all documentation."""
        search_index = []
        for module_name, data in self.module_data.items():
            search_index.append({
                "title": module_name,
                "content": data["docstring"],
                "url": f"/{module_name}.html"
            })
            for func in data["functions"]:
                search_index.append({
                    "title": f"{module_name}.{func['name']}",
                    "content": func["docstring"],
                    "url": f"/{module_name}.html#{func['name']}"
                })
        return search_index
    
    def generate_html(self):
        """Generate HTML files for the documentation."""
        try:
            # Create output directory
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
            self.output_dir.mkdir()
            
            # Copy static assets
            shutil.copytree(self.template_dir / "static", self.output_dir / "static")
            
            # Generate index.html
            with open(self.template_dir / "index.html", "r") as f:
                index_template = f.read()
                
            with open(self.output_dir / "index.html", "w") as f:
                f.write(index_template.replace("{{searchIndex}}", json.dumps(self.generate_search_index())))
                
            # Generate module pages
            for module_name, data in self.module_data.items():
                with open(self.template_dir / "module.html", "r") as f:
                    module_template = f.read()
                    
                content = f"<h1>{module_name}</h1>"
                content += f"<p>{data['docstring']}</p>"
                
                if data["functions"]:
                    content += "<h2>Functions</h2>"
                    for func in data["functions"]:
                        content += f"""
                        <div class="function" id="{func['name']}">
                            <h3>{func['name']}({func['params']})</h3>
                            <p>{func['docstring']}</p>
                        </div>
                        """
                        
                with open(self.output_dir / f"{module_name}.html", "w") as f:
                    f.write(module_template.replace("{{content}}", content))
                    
        except OSError as e:
            if e.errno == 28:  # No space left on device
                print("Error: No space left on device. Please free up some disk space.")
            else:
                print(f"Error generating HTML: {str(e)}")
            raise
                
    def update_online_documentation(self):
        """Main function to update the online documentation."""
        try:
            # Parse all Python files
            for file in self.base_dir.glob("*.py"):
                if file.name != "__init__.py" and file.name != "WEBSITE.py":
                    self.module_data[file.stem] = self.parse_module(file)
                    
            # Generate documentation
            self.generate_html()
            print("Documentation generated successfully!")
            print(f"Documentation saved to: {self.output_dir}")
            
        except Exception as e:
            print(f"Error updating documentation: {str(e)}")
            raise

if __name__ == "__main__":
    generator = DocumentationGenerator()
    generator.update_online_documentation()
