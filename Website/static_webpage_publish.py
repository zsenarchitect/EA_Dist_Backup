import os
import json
import shutil
import sys
import markdown
from pathlib import Path

# Add the lib folder to the path to import EnneadTab modules
current_dir = Path(__file__).parent
# Try to find Apps/lib folder in different possible locations
possible_lib_paths = [
    current_dir.parent / "Apps" / "lib",  # When in main repo: ../Apps/lib
    current_dir / ".." / ".." / "Apps" / "lib",  # Alternative path
    Path.cwd() / "Apps" / "lib",  # When run from repo root
]

lib_folder = None
for path in possible_lib_paths:
    if path.exists():
        lib_folder = path
        break

if lib_folder:
    sys.path.insert(0, str(lib_folder))
else:
    print("Warning: Apps/lib folder not found in any expected location")

try:
    import EnneadTab.DOCUMENTATION as DOCUMENTATION
    import EnneadTab.DATA_FILE as DATA_FILE
    import EnneadTab.ENVIRONMENT as ENVIRONMENT
    HAS_ENNEAD_MODULES = True
    print("Successfully imported EnneadTab modules")
except ImportError as e:
    print(f"Warning: EnneadTab modules not found: {e}")
    HAS_ENNEAD_MODULES = False

def get_knowledge_data_fallback(app):
    """Fallback method to get knowledge data when EnneadTab modules are not available."""
    # Try to find knowledge files in different possible locations
    possible_apps_paths = [
        current_dir.parent / "Apps",  # When in main repo: ../Apps
        Path.cwd() / "Apps",  # When run from repo root
    ]
    
    knowledge_files = {}
    for apps_path in possible_apps_paths:
        if apps_path.exists():
            knowledge_files = {
                "Rhino": apps_path / "_rhino" / "knowledge_rhino_database.sexyDuck",
                "Revit": apps_path / "_revit" / "knowledge_revit_database.sexyDuck"
            }
            break
    
    file_path = knowledge_files.get(app)
    if file_path and file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {app} knowledge data: {e}")
    
    return {}

def get_knowledge_data(app):
    """Get knowledge data using DOCUMENTATION module functions."""
    if not HAS_ENNEAD_MODULES:
        return get_knowledge_data_fallback(app)
    
    try:
        if app == "Rhino":
            # Use DOCUMENTATION module's get_rhino_knowledge function
            return DOCUMENTATION.get_rhino_knowledge()
        elif app == "Revit":
            # For Revit, first update the knowledge base, then get it
            DOCUMENTATION.set_revit_knowledge()
            return DOCUMENTATION.get_revit_knowledge()
    except Exception as e:
        print(f"Error using DOCUMENTATION module for {app}: {e}")
        return get_knowledge_data_fallback(app)
    
    return {}

def get_raw_knowledge_data(app):
    """Get raw knowledge data (before sanitization) using DOCUMENTATION module."""
    if not HAS_ENNEAD_MODULES:
        return get_knowledge_data_fallback(app)
    
    try:
        if app == "Rhino":
            return DATA_FILE.get_data(ENVIRONMENT.KNOWLEDGE_RHINO_FILE)
        elif app == "Revit":
            # Ensure Revit knowledge is up to date
            DOCUMENTATION.set_revit_knowledge()
            return DATA_FILE.get_data(ENVIRONMENT.KNOWLEDGE_REVIT_FILE)
    except Exception as e:
        print(f"Error getting raw knowledge data for {app}: {e}")
        return get_knowledge_data_fallback(app)
    
    return {}

def organize_by_tab_using_documentation_logic(app):
    """Organize knowledge data using the same logic as DOCUMENTATION.generate_app_documentation."""
    if not HAS_ENNEAD_MODULES:
        # Fallback to basic organization
        knowledge_data = get_knowledge_data_fallback(app)
        return organize_by_tab_fallback(knowledge_data)
    
    try:
        # Get both raw and sanitized data
        raw_knowledge = get_raw_knowledge_data(app)
        knowledge_dict = get_knowledge_data(app)
        
        # Use the same delayed item keywords as DOCUMENTATION module
        delayed_item_keywords = ["browser", "contents", "proj", "personal", "tester", "archive"]
        
        # Use the same sorting logic as DOCUMENTATION.generate_app_documentation
        def get_command_order(x):
            tab = x.get("tab")
            commands = x.get("alias")
            if not isinstance(commands, list):
                commands = [commands]

            if not tab:
                tab = "no tab"
            
            def is_in_delayed_category(x):
                for item in delayed_item_keywords:
                    if item in x.lower():
                        return True
                return False
            
            return "{}, {}, {}".format(is_in_delayed_category(tab), tab, commands)
        
        # Sort using DOCUMENTATION module's logic
        app_knowledge = sorted(knowledge_dict.values(), key=get_command_order)
        
        # Organize into tabs
        tabs = {}
        for tool_data in app_knowledge:
            tab_name = tool_data.get("tab", "No Tab")
            if not tab_name or tab_name == "No Tab":
                tab_name = "Utilities"
                
            # Clean up tab name (same as DOCUMENTATION module)
            tab_name = tab_name.replace(".panel", "").replace(".tab", "")
            
            if tab_name not in tabs:
                tabs[tab_name] = {
                    "name": tab_name,
                    "icon": tool_data.get("tab_icon", ""),
                    "tools": [],
                    "is_delayed": any(keyword in tab_name.lower() for keyword in delayed_item_keywords)
                }
            
            tabs[tab_name]["tools"].append(tool_data)
        
        return tabs
        
    except Exception as e:
        print(f"Error organizing data using DOCUMENTATION logic: {e}")
        # Fallback to basic organization
        knowledge_data = get_knowledge_data_fallback(app)
        return organize_by_tab_fallback(knowledge_data)

def organize_by_tab_fallback(knowledge_data):
    """Fallback organization method when DOCUMENTATION module is not available."""
    tabs = {}
    delayed_keywords = ["browser", "contents", "proj", "personal", "tester", "archive"]
    
    def is_delayed_tab(tab_name):
        return any(keyword in tab_name.lower() for keyword in delayed_keywords)
    
    for script_path, data in knowledge_data.items():
        tab_name = data.get("tab", "No Tab")
        if not tab_name or tab_name == "No Tab":
            tab_name = "Utilities"
            
        tab_name = tab_name.replace(".panel", "").replace(".tab", "")
        
        if tab_name not in tabs:
            tabs[tab_name] = {
                "name": tab_name,
                "icon": data.get("tab_icon", ""),
                "tools": [],
                "is_delayed": is_delayed_tab(tab_name)
            }
        
        tool_data = {
            "script": data.get("script", ""),
            "alias": data.get("alias", "Unknown Command"),
            "doc": data.get("doc", "No documentation available."),
            "icon": data.get("icon", ""),
            "is_popular": data.get("is_popular", False)
        }
        
        tabs[tab_name]["tools"].append(tool_data)
    
    # Sort tools within each tab by popularity and then alphabetically
    for tab_data in tabs.values():
        # Fix the sorting issue by ensuring alias is always a string
        tab_data["tools"].sort(key=lambda x: (not x["is_popular"], str(x["alias"]) if x["alias"] else ""))
    
    return tabs

def count_tailor_scripts(app):
    """Count tailor scripts using the same logic as DOCUMENTATION module."""
    if not HAS_ENNEAD_MODULES:
        return 0
    
    try:
        raw_knowledge = get_raw_knowledge_data(app)
        
        # Use the same tailor counting logic as DOCUMENTATION.generate_app_documentation
        import re
        tailor_count = 0
        for v in raw_knowledge.values():
            script = v.get("script", "")
            parts = re.split(r"[\\\\/]+", script)
            for part in parts:
                if "tailor" in part.lower():
                    tailor_count += 1
                    break
        
        return tailor_count
    except Exception as e:
        print(f"Error counting tailor scripts: {e}")
        return 0

def generate_html_content(app, tabs_data):
    """Generate HTML content for the documentation page."""
    # Get tailor count using DOCUMENTATION module logic
    tailor_count = count_tailor_scripts(app)
    
    # Set active nav link
    nav_links = {
        "rhino": {"rhino": "active", "revit": "", "installation": ""},
        "revit": {"rhino": "", "revit": "active", "installation": ""},
    }
    active_nav = nav_links.get(app.lower(), {"rhino": "", "revit": "", "installation": ""})
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EnneadTab {app} Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-box-seam me-2"></i>EnneadTab
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link {active_nav['rhino']}" href="rhino.html">
                            <i class="bi bi-pencil-square me-1"></i>Rhino
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_nav['revit']}" href="revit.html">
                            <i class="bi bi-building me-1"></i>Revit
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_nav['installation']}" href="installation.html">
                            <i class="bi bi-download me-1"></i>Installation
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5 pt-5">
        <div class="row">
            <div class="col-md-3">
                <div class="toc">
                    <h5>Table of Contents</h5>
                    <div class="search-box mb-3">
                        <input type="text" class="form-control" id="searchInput" placeholder="Search tools...">
                    </div>
                    <ul class="nav flex-column">
"""
    
    # Add table of contents
    for tab_name, tab_data in tabs_data.items():
        tool_count = len(tab_data["tools"])
        popular_count = sum(1 for tool in tab_data["tools"] if tool.get("is_popular", False))
        
        html += f"""
                        <li class="nav-item">
                            <a class="nav-link" href="#{tab_name.lower().replace(' ', '-').replace('.', '')}">
                                <i class="bi bi-folder me-2"></i>{tab_name}
                                <span class="badge bg-secondary ms-2">{tool_count}</span>
                                {f'<span class="badge bg-warning ms-1">{popular_count}</span>' if popular_count > 0 else ''}
                            </a>
                        </li>"""

    html += f"""
                    </ul>
                    {f'<div class="mt-3"><small class="text-muted">Note: {tailor_count} tailor scripts excluded from documentation</small></div>' if tailor_count > 0 else ''}
                </div>
            </div>
            <div class="col-md-9">
                <div class="doc-section">
                    <h1 class="mb-4">{app} Documentation</h1>
                    <p class="lead">Comprehensive documentation for EnneadTab {app} tools. Use the search box or browse by category.</p>
"""

    # Add content for each tab
    for tab_name, tab_data in tabs_data.items():
        tab_id = tab_name.lower().replace(' ', '-').replace('.', '')
        html += f"""
                    <section id="{tab_id}" class="content-section">
                        <h2><i class="bi bi-folder me-2"></i>{tab_name}</h2>
                        <div class="card hover-card">
                            <div class="card-body">
                                <div class="tools-grid">
"""
        
        for tool in tab_data["tools"]:
            # Handle both string and list aliases (same as DOCUMENTATION module)
            alias = tool.get('alias', 'Unknown Command')
            if isinstance(alias, list):
                alias = alias[0] if alias else "Unknown Command"
            
            # Clean up documentation
            doc = tool.get('doc', 'No documentation available.')
            if not doc or doc == "Doc string not set":
                doc = "No documentation available for this tool."
            
            # Disable popular status - set all tools as unpopular
            is_popular = False  # Force all tools to be unpopular
            popular_badge = ''  # Remove popular badge completely
            
            html += f"""
                                    <div class="tool-card" data-search="{alias.lower()} {doc.lower()}">
                                        <h5>
                                            <i class="bi bi-command me-2"></i>{alias}
                                            {popular_badge}
                                        </h5>
                                        <p>{doc}</p>
                                        <div class="bg-dark p-3 rounded">
                                            <code>Command: {alias}</code>
                                        </div>
                                    </div>
"""
        
        html += """
                                </div>
                            </div>
                        </div>
                    </section>
"""

    html += """
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>EnneadTab Documentation</h5>
                    <p>Made with love by the EnneadTab team</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="https://github.com/Ennead-Architects-LLP/EnneadTab-OS" class="text-light me-3">
                        <i class="bi bi-github"></i> GitHub
                    </a>
                    <a href="https://github.com/Ennead-Architects-LLP/EA_Dist" class="text-light">
                        <i class="bi bi-box-seam"></i> Distribution
                    </a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
    
    return html

def generate_index_html():
    """Generate the main index.html page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EnneadTab Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-box-seam me-2"></i>EnneadTab
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="rhino.html">
                            <i class="bi bi-pencil-square me-1"></i>Rhino
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="revit.html">
                            <i class="bi bi-building me-1"></i>Revit
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="installation.html">
                            <i class="bi bi-download me-1"></i>Installation
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="hero">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1>EnneadTab</h1>
                    <p class="lead">Powerful tools for Rhino and Revit to streamline your architectural workflow</p>
                    <div class="mt-4">
                        <a href="rhino.html" class="btn btn-primary me-3">
                            <i class="bi bi-pencil-square me-2"></i>Rhino Tools
                        </a>
                        <a href="revit.html" class="btn btn-primary me-3">
                            <i class="bi bi-building me-2"></i>Revit Tools
                        </a>
                        <a href="https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe" class="btn btn-outline-primary" target="_blank" rel="noopener noreferrer">
                            <i class="bi bi-download me-2"></i>Download
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card hover-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-pencil-square display-4 text-primary mb-3"></i>
                        <h5 class="card-title">Rhino Tools</h5>
                        <p class="card-text">Comprehensive set of tools for Rhino 3D modeling and design workflows.</p>
                        <a href="rhino.html" class="btn btn-primary">Explore Rhino Tools</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card hover-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-building display-4 text-primary mb-3"></i>
                        <h5 class="card-title">Revit Tools</h5>
                        <p class="card-text">Advanced tools for Revit BIM workflows and architectural documentation.</p>
                        <a href="revit.html" class="btn btn-primary">Explore Revit Tools</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card hover-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-download display-4 text-primary mb-3"></i>
                        <h5 class="card-title">Installation</h5>
                        <p class="card-text">Get started with EnneadTab by following our installation guide.</p>
                        <a href="installation.html" class="btn btn-primary">Installation Guide</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>EnneadTab Documentation</h5>
                    <p>Made with love by the EnneadTab team</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="https://github.com/Ennead-Architects-LLP/EnneadTab-OS" class="text-light me-3">
                        <i class="bi bi-github"></i> GitHub
                    </a>
                    <a href="https://github.com/Ennead-Architects-LLP/EA_Dist" class="text-light">
                        <i class="bi bi-box-seam"></i> Distribution
                    </a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
    return html

def generate_installation_html():
    """Generate the installation.html page from markdown file."""
    # Read the markdown file
    md_file_path = current_dir / "Installation" / "How To Install.md"
    
    if md_file_path.exists():
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to HTML
            html_content = markdown.markdown(md_content, extensions=['toc', 'tables', 'fenced_code'])
        except Exception as e:
            print(f"Error reading markdown file: {e}")
            html_content = "<p>Installation guide content could not be loaded.</p>"
    else:
        html_content = "<p>Installation guide not found.</p>"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EnneadTab Installation Guide</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-box-seam me-2"></i>EnneadTab
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="rhino.html">
                            <i class="bi bi-pencil-square me-1"></i>Rhino
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="revit.html">
                            <i class="bi bi-building me-1"></i>Revit
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="installation.html">
                            <i class="bi bi-download me-1"></i>Installation
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5 pt-5">
        <div class="doc-section">
            <div class="installation-content">
                {html_content}
            </div>
            
            <div class="mt-5">
                <h2>Quick Links</h2>
                <div class="row">
                    <div class="col-md-6">
                        <div class="info-box">
                            <h5><i class="bi bi-download me-2"></i>Download EnneadTab</h5>
                            <p>Get the latest version from our distribution repository:</p>
                            <a href="https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe" class="btn btn-primary" target="_blank" rel="noopener noreferrer">
                                <i class="bi bi-download me-2"></i>Download Installer
                            </a>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-box">
                            <h5><i class="bi bi-question-circle me-2"></i>Need Help?</h5>
                            <p>If you encounter any issues:</p>
                            <a href="https://github.com/Ennead-Architects-LLP/EnneadTab-OS/issues" class="btn btn-outline-primary" target="_blank" rel="noopener noreferrer">
                                <i class="bi bi-bug me-2"></i>Report Issues
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>EnneadTab Documentation</h5>
                    <p>Made with love by the EnneadTab team</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="https://github.com/Ennead-Architects-LLP/EnneadTab-OS" class="text-light me-3" target="_blank" rel="noopener noreferrer">
                        <i class="bi bi-github"></i> GitHub
                    </a>
                    <a href="https://github.com/Ennead-Architects-LLP/EA_Dist" class="text-light" target="_blank" rel="noopener noreferrer">
                        <i class="bi bi-box-seam"></i> Distribution
                    </a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
    return html

def update_documentation():
    """Update documentation by copying HTML files and assets to docs directory."""
    print("Starting documentation update...")
    
    # Create docs directory if it doesn't exist
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Copy static assets if they exist
    assets_dir = Path("Website/assets")
    if assets_dir.exists():
        shutil.copytree(assets_dir, docs_dir / "assets", dirs_exist_ok=True)
        print("Copied assets")
    
    # Copy CSS and JS files from existing docs directory if they exist
    for file in ["styles.css", "script.js"]:
        # Try current directory first (when script is in Website folder)
        source_file = Path(file)
        if not source_file.exists():
            # Try docs subfolder
            source_file = Path(f"docs/{file}")
        if not source_file.exists():
            # Try Website folder (when script is run from parent directory)
            source_file = Path(f"Website/{file}")
            
        if source_file.exists():
            shutil.copy(source_file, docs_dir)
            print(f"Copied {file} from {source_file}")
        else:
            print(f"Warning: {file} not found in any expected location")
    
    # Generate documentation for each app using DOCUMENTATION module logic
    for app in ["Rhino", "Revit"]:
        print(f"Generating {app} documentation using DOCUMENTATION module...")
        
        try:
            # Use DOCUMENTATION module's organization logic
            tabs_data = organize_by_tab_using_documentation_logic(app)
            
            if not tabs_data:
                print(f"Warning: No tabs data generated for {app}")
                continue
                
            print(f"Organized into {len(tabs_data)} tabs for {app}")
            
            # Generate HTML content
            html_content = generate_html_content(app, tabs_data)
            
            # Write HTML file
            output_file = docs_dir / f"{app.lower()}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"Generated {output_file}")
            
        except Exception as e:
            print(f"Error generating {app} documentation: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate static pages
    print("Generating static pages...")
    
    # Generate index.html
    index_content = generate_index_html()
    with open(docs_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    print("Generated index.html")
    
    # Generate installation.html
    installation_content = generate_installation_html()
    with open(docs_dir / "installation.html", "w", encoding="utf-8") as f:
        f.write(installation_content)
    print("Generated installation.html")
    
    print("Documentation update completed!")

def commit_and_push():
    """Commit changes and push to GitHub."""
    import subprocess
    
    try:
        # Check if we're in a git repository
        subprocess.run(["git", "status"], check=True, capture_output=True)
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        print("Added files to git")
        
        # Commit changes
        result = subprocess.run(["git", "commit", "-m", "Update documentation"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Committed changes")
        else:
            print("No changes to commit or commit failed")
            print(result.stdout)
            print(result.stderr)
        
        # Check if gh-pages branch exists
        branch_check = subprocess.run(["git", "branch", "-r"], 
                                    capture_output=True, text=True)
        
        if "origin/gh-pages" in branch_check.stdout:
            # gh-pages branch exists, push to it
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Pushed to main branch")
        else:
            # gh-pages branch doesn't exist, just push to main
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Pushed to main branch (gh-pages branch will be created by GitHub Actions)")
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        # Don't raise the error, just log it
    except Exception as e:
        print(f"Unexpected error during git operations: {e}")

if __name__ == "__main__":
    update_documentation()
    commit_and_push() 