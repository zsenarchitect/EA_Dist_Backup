import os
import json
import shutil
import sys
import markdown
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

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
        print(f"Found lib folder at: {path}")
        break

if lib_folder:
    sys.path.insert(0, str(lib_folder))
    print(f"Added {lib_folder} to Python path")
else:
    print("Warning: Apps/lib folder not found in any expected location")
    print("Searched in:")
    for path in possible_lib_paths:
        print(f"  - {path}")

try:
    import EnneadTab.DOCUMENTATION as DOCUMENTATION
    import EnneadTab.DATA_FILE as DATA_FILE
    import EnneadTab.ENVIRONMENT as ENVIRONMENT
    HAS_ENNEAD_MODULES = True
    print("Successfully imported EnneadTab modules")
except ImportError as e:
    print(f"Warning: EnneadTab modules not found: {e}")
    print("The script will continue with limited functionality")
    HAS_ENNEAD_MODULES = False

# GitHub Pages Configuration
GITHUB_PAGES_CONFIG = {
    "custom_domain": "",  # Set this to your custom domain if needed, e.g., "docs.yourcompany.com"
    "repo_name": "EnneadTab-OS",  # Will be auto-detected if possible
    "organization": "Ennead-Architects-LLP",  # Will be auto-detected if possible
    "site_url": "",  # Will be constructed automatically
    "enable_jekyll": False,  # Set to True if you want Jekyll processing
    "enable_sitemap": True,
    "enable_robots_txt": True,
    "enable_404_page": True
}

def get_current_year():
    """Get the current year for dynamic copyright."""
    return datetime.now().year

def detect_github_config():
    """Auto-detect GitHub repository configuration."""
    global GITHUB_PAGES_CONFIG
    
    try:
        import subprocess
        
        # Get remote origin URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True
        )
        
        remote_url = result.stdout.strip()
        print(f"Detected remote URL: {remote_url}")
        
        # Parse GitHub URL
        if "github.com" in remote_url:
            # Handle both HTTPS and SSH URLs
            if remote_url.startswith("https://"):
                # https://github.com/org/repo.git
                parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
            elif remote_url.startswith("git@"):
                # git@github.com:org/repo.git
                parts = remote_url.replace("git@github.com:", "").replace(".git", "").split("/")
            else:
                return
            
            if len(parts) >= 2:
                GITHUB_PAGES_CONFIG["organization"] = parts[0]
                GITHUB_PAGES_CONFIG["repo_name"] = parts[1]
                
                # Construct site URL
                if GITHUB_PAGES_CONFIG["custom_domain"]:
                    GITHUB_PAGES_CONFIG["site_url"] = f"https://{GITHUB_PAGES_CONFIG['custom_domain']}"
                else:
                    GITHUB_PAGES_CONFIG["site_url"] = f"https://{parts[0]}.github.io/{parts[1]}"
                
                print(f"Auto-detected: {parts[0]}/{parts[1]}")
                print(f"Site URL: {GITHUB_PAGES_CONFIG['site_url']}")
    
    except Exception as e:
        print(f"Could not auto-detect GitHub config: {e}")
        # Use defaults
        if not GITHUB_PAGES_CONFIG["site_url"]:
            GITHUB_PAGES_CONFIG["site_url"] = f"https://{GITHUB_PAGES_CONFIG['organization']}.github.io/{GITHUB_PAGES_CONFIG['repo_name']}"

def create_github_pages_files(docs_dir):
    """Create necessary GitHub Pages configuration files."""
    print("Creating GitHub Pages configuration files...")
    
    # Create .nojekyll file if Jekyll is disabled
    if not GITHUB_PAGES_CONFIG["enable_jekyll"]:
        nojekyll_file = docs_dir / ".nojekyll"
        nojekyll_file.touch()
        print("Created .nojekyll file")
    
    # Create CNAME file for custom domain
    if GITHUB_PAGES_CONFIG["custom_domain"]:
        cname_file = docs_dir / "CNAME"
        with open(cname_file, "w", encoding="utf-8") as f:
            f.write(GITHUB_PAGES_CONFIG["custom_domain"])
        print(f"Created CNAME file for {GITHUB_PAGES_CONFIG['custom_domain']}")
    
    # Create robots.txt
    if GITHUB_PAGES_CONFIG["enable_robots_txt"]:
        create_robots_txt(docs_dir)
    
    # Create sitemap.xml
    if GITHUB_PAGES_CONFIG["enable_sitemap"]:
        create_sitemap_xml(docs_dir)
    
    # Create 404.html
    if GITHUB_PAGES_CONFIG["enable_404_page"]:
        create_404_page(docs_dir)

def create_robots_txt(docs_dir):
    """Create robots.txt file for SEO."""
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {GITHUB_PAGES_CONFIG['site_url']}/sitemap.xml
"""
    
    robots_file = docs_dir / "robots.txt"
    with open(robots_file, "w", encoding="utf-8") as f:
        f.write(robots_content)
    print("Created robots.txt")

def create_sitemap_xml(docs_dir):
    """Create sitemap.xml for SEO."""
    # Define the pages that should be in sitemap
    pages = [
        {"url": "", "priority": "1.0", "changefreq": "weekly"},  # index.html
        {"url": "rhino.html", "priority": "0.9", "changefreq": "weekly"},
        {"url": "revit.html", "priority": "0.9", "changefreq": "weekly"},
        {"url": "installation.html", "priority": "0.8", "changefreq": "monthly"},
    ]
    
    # Create XML structure
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    for page in pages:
        url_elem = ET.SubElement(urlset, "url")
        
        # Create full URL
        full_url = f"{GITHUB_PAGES_CONFIG['site_url']}/{page['url']}" if page['url'] else GITHUB_PAGES_CONFIG['site_url']
        
        loc_elem = ET.SubElement(url_elem, "loc")
        loc_elem.text = full_url
        
        lastmod_elem = ET.SubElement(url_elem, "lastmod")
        lastmod_elem.text = datetime.now().strftime("%Y-%m-%d")
        
        changefreq_elem = ET.SubElement(url_elem, "changefreq")
        changefreq_elem.text = page["changefreq"]
        
        priority_elem = ET.SubElement(url_elem, "priority")
        priority_elem.text = page["priority"]
    
    # Write XML file
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ", level=0)  # Pretty print
    
    sitemap_file = docs_dir / "sitemap.xml"
    tree.write(sitemap_file, encoding="utf-8", xml_declaration=True)
    print("Created sitemap.xml")

def create_404_page(docs_dir):
    """Create custom 404.html page."""
    html_404 = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | EnneadTab Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
    <meta name="robots" content="noindex">
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

    <div class="container my-5 pt-5">
        <div class="text-center" style="margin-top: 100px;">
            <div class="hero" style="padding: 4rem 0;">
                <h1 style="font-size: 6rem; font-weight: 800; color: var(--secondary-color);">404</h1>
                <h2 style="font-size: 2rem; margin-bottom: 2rem;">Page Not Found</h2>
                <p style="font-size: 1.2rem; color: var(--text-muted); margin-bottom: 3rem;">
                    Sorry, the page you're looking for doesn't exist or has been moved.
                </p>
                <div class="d-flex justify-content-center gap-3 flex-wrap">
                    <a href="index.html" class="btn btn-primary btn-lg">
                        <i class="bi bi-house me-2"></i>Go Home
                    </a>
                    <a href="rhino.html" class="btn btn-outline-primary btn-lg">
                        <i class="bi bi-pencil-square me-2"></i>Rhino Tools
                    </a>
                    <a href="revit.html" class="btn btn-outline-primary btn-lg">
                        <i class="bi bi-building me-2"></i>Revit Tools
                    </a>
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
                    <a href="https://github.com/{GITHUB_PAGES_CONFIG['organization']}/EnneadTab-OS" class="text-light me-3" target="_blank" rel="noopener noreferrer">
                        <i class="bi bi-github"></i> GitHub
                    </a>
                    <a href="https://github.com/{GITHUB_PAGES_CONFIG['organization']}/EA_Dist" class="text-light" target="_blank" rel="noopener noreferrer">
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
    
    error_404_file = docs_dir / "404.html"
    with open(error_404_file, "w", encoding="utf-8") as f:
        f.write(html_404)
    print("Created 404.html")

def create_github_actions_workflow():
    """Create GitHub Actions workflow for automatic deployment."""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = """name: Deploy Documentation to GitHub Pages

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install markdown
        
    - name: Generate documentation
      run: |
        cd Website
        python static_webpage_publish.py
        
    - name: Setup Pages
      uses: actions/configure-pages@v3
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: './Website/docs'

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
"""
    
    workflow_file = workflow_dir / "deploy-docs.yml"
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write(workflow_content)
    print("Created GitHub Actions workflow")

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
        tab_data["tools"].sort(key=lambda x: (not x.get("is_popular", False), x.get("alias", "").lower()))
    
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

    # Determine app-specific guidance
    app_guidance = {
        "Rhino": {
            "activation_method": "Left-click or Right-click to access commands",
            "interface_type": "Commands",
            "instruction_prefix": "Command:"
        },
        "Revit": {
            "activation_method": "Left-click buttons in the ribbon",
            "interface_type": "Buttons", 
            "instruction_prefix": "Button:"
        }
    }
    
    current_app_guidance = app_guidance.get(app, app_guidance["Rhino"])

    # Add content for each tab
    for tab_name, tab_data in tabs_data.items():
        tab_id = tab_name.lower().replace(' ', '-').replace('.', '')
        
        # Get tab icon information
        tab_icon = tab_data.get("icon", "")
        icon_info = f"Look for the <i class='bi bi-{tab_icon}'></i> icon." if tab_icon else "Tab icon may vary."
        
        html += f"""
                    <section id="{tab_id}" class="content-section">
                        <h2><i class="bi bi-{tab_icon if tab_icon else 'folder'} me-2"></i>{tab_name}</h2>
                        <div class="info-box mb-4">
                            <h6><i class="bi bi-lightbulb me-2"></i>How to find this tab:</h6>
                            <p class="mb-2">Look for the <strong>{tab_name}</strong> tab in your {app} {'toolbar' if app == 'Rhino' else 'ribbon'}. {icon_info}</p>
                            <p class="mb-0"><strong>Activation:</strong> {current_app_guidance['activation_method']}</p>
                        </div>
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
                                            <i class="bi bi-{'terminal' if app == 'Rhino' else 'square'} me-2"></i>{alias}
                                            {popular_badge}
                                        </h5>
                                        <p>{doc}</p>
                                        <div class="bg-dark p-3 rounded">
                                            <code>{current_app_guidance['instruction_prefix']} {alias}</code>
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
    current_year = get_current_year()
    html = f"""<!DOCTYPE html>
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
    print("=" * 60)
    
    # Auto-detect GitHub configuration
    detect_github_config()
    
    # Create docs directory if it doesn't exist
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Create GitHub Pages configuration files
    create_github_pages_files(docs_dir)
    
    # Create GitHub Actions workflow (in parent directory)
    create_github_actions_workflow()
    
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
    
    # Create setup guide for distribution repositories
    create_setup_guide()
    
    print("=" * 60)
    print("🎉 Documentation update completed!")
    print(f"🌐 Site URL: {GITHUB_PAGES_CONFIG['site_url']}")
    print("📁 Files generated in: ./docs/")
    print("🚀 GitHub Actions workflow created for auto-deployment")
    print("📖 Setup guide created: GITHUB_PAGES_SETUP.md")
    print("=" * 60)

def create_setup_guide():
    """Create a setup guide for distribution repositories."""
    setup_guide = """# GitHub Pages Setup Guide for Distribution Repositories

## Automatic Setup
This script automatically configures GitHub Pages for your repository. Here's what it creates:

### Files Created:
- `.nojekyll` - Disables Jekyll processing for faster builds
- `404.html` - Custom 404 error page
- `robots.txt` - SEO configuration for search engines
- `sitemap.xml` - Site map for better SEO
- `.github/workflows/deploy-docs.yml` - GitHub Actions workflow for auto-deployment

### Repository Configuration Required:
1. Go to your repository Settings
2. Navigate to Pages section
3. Set Source to "GitHub Actions"
4. The workflow will automatically deploy on push to main/master

### Custom Domain Setup (Optional):
1. Update the `custom_domain` in the GITHUB_PAGES_CONFIG
2. Add a CNAME record in your DNS pointing to: [username].github.io
3. The script will automatically create the CNAME file

### For Distribution Repositories:
1. Copy this entire Website folder to your distribution repository
2. Update the GITHUB_PAGES_CONFIG with your repository details
3. Run `python static_webpage_publish.py`
4. Enable GitHub Pages in repository settings

### Troubleshooting:
- If site appears empty, check GitHub Pages source is set to "GitHub Actions"
- Ensure the workflow has permissions to deploy (check repository Settings > Actions)
- Verify all required files are in the docs/ folder

### URLs:
- Repository: https://github.com/{GITHUB_PAGES_CONFIG['organization']}/{GITHUB_PAGES_CONFIG['repo_name']}
- Live Site: {GITHUB_PAGES_CONFIG['site_url']}
"""
    
    setup_file = Path("GITHUB_PAGES_SETUP.md")
    with open(setup_file, "w", encoding="utf-8") as f:
        f.write(setup_guide)
    print("Created GitHub Pages setup guide: GITHUB_PAGES_SETUP.md")

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
        result = subprocess.run(["git", "commit", "-m", "Update documentation with GitHub Pages config"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Committed changes")
        else:
            print("No changes to commit or commit failed")
            print(result.stdout)
            print(result.stderr)
        
        # Push to main branch
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Pushed to main branch")
        except subprocess.CalledProcessError:
            # Try master branch if main doesn't exist
            try:
                subprocess.run(["git", "push", "origin", "master"], check=True)
                print("Pushed to master branch")
            except subprocess.CalledProcessError:
                print("Failed to push - check branch name and permissions")
        
        print("\n🎯 Next Steps:")
        print("1. Go to your repository Settings → Pages")
        print("2. Set Source to 'GitHub Actions'")
        print("3. Wait for the workflow to complete")
        print(f"4. Visit your site at: {GITHUB_PAGES_CONFIG['site_url']}")
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        # Don't raise the error, just log it
    except Exception as e:
        print(f"Unexpected error during git operations: {e}")

if __name__ == "__main__":
    update_documentation()
    commit_and_push() 