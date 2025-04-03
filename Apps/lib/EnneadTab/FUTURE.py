"""
Scripts that need to be updated to remove hardcoded "4b_Applied Computing" paths.
This collection is automatically generated and should be reviewed periodically.

Purpose:
- Track scripts that need path standardization
- Plan future updates to make codebase more portable
- Identify dependencies on specific network locations

Last Updated: 2025-04-03 16:49:10
"""

import os
import re
import sys
import time
import json
from datetime import datetime

def get_json_path():
    """Get the path to the JSON file storing hardcoded paths."""
    return os.path.join(os.path.dirname(__file__), 'hardcoded_paths.json')

def load_hardcoded_paths():
    """Load hardcoded paths from JSON file.
    
    Returns:
        tuple: (list of paths, dict of categorized paths, last updated timestamp)
    """
    json_path = get_json_path()
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            # Flatten categories into a single list
            all_paths = []
            for category_data in data['categories'].values():
                all_paths.extend(category_data.keys())
            return all_paths, data['categories'], data['last_updated']
    except Exception as e:
        print("Error loading JSON: {}".format(str(e)))
        return [], {}, None

def save_hardcoded_paths(categories):
    """Save hardcoded paths to JSON file.
    
    Args:
        categories (dict): Dictionary of categorized paths with line numbers
    """
    json_path = get_json_path()
    data = {
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'categories': categories
    }
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_scripts_with_hardcoded_paths():
    """Return the list of scripts that contain hardcoded '4b_Applied Computing' paths.
    
    Returns:
        list: List of script paths that need to be updated to remove hardcoded paths.
    """
    paths, _, _ = load_hardcoded_paths()
    return paths

def is_script_using_hardcoded_paths(script_path):
    """Check if a given script is in the list of scripts using hardcoded paths.
    
    Args:
        script_path (str): Path to the script to check
        
    Returns:
        bool: True if script uses hardcoded paths, False otherwise
    """
    return script_path in get_scripts_with_hardcoded_paths()

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    """Print progress bar in terminal.
    
    Args:
        iteration (int): Current iteration
        total (int): Total iterations
        prefix (str): Prefix string
        suffix (str): Suffix string
        decimals (int): Positive number of decimals in percent complete
        length (int): Character length of bar
        fill (str): Bar fill character
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total: 
        print()

def find_hardcoded_lines(content, pattern):
    """Find line numbers containing hardcoded paths in content.
    
    Args:
        content (str): File content to search
        pattern (re.Pattern): Compiled regex pattern to search for
        
    Returns:
        list: List of line numbers (1-indexed) containing matches
    """
    lines = content.split('\n')
    line_numbers = []
    for i, line in enumerate(lines, 1):
        if pattern.search(line):
            line_numbers.append(i)
    return line_numbers

def scan_repo_for_hardcoded_paths(repo_root=None):
    """Scan the repository for files containing hardcoded '4b_Applied Computing' paths.
    
    Args:
        repo_root (str, optional): Root directory of the repository. Defaults to current directory.
        
    Returns:
        dict: Dictionary of categorized paths with line numbers
    """
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    hardcoded_scripts = {}
    pattern = re.compile(r'4b_Applied Computing', re.IGNORECASE)
    
    # Count total Python files first
    total_files = 0
    for root, _, files in os.walk(repo_root):
        total_files += len([f for f in files if f.endswith('.py')])
    
    current_file = 0
    print_progress_bar(0, total_files, prefix='Scanning:', suffix='Complete')
    
    for root, _, files in os.walk(repo_root):
        for file in files:
            if file.endswith('.py'):
                current_file += 1
                print_progress_bar(current_file, total_files, prefix='Scanning:', suffix='Complete')
                
                file_path = os.path.join(root, file)
                try:
                    # Try different encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252']
                    content = None
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content and pattern.search(content):
                        # Convert to relative path
                        rel_path = os.path.relpath(file_path, repo_root)
                        # Normalize path separators
                        rel_path = rel_path.replace('\\', '/')
                        # Find line numbers
                        line_numbers = find_hardcoded_lines(content, pattern)
                        hardcoded_scripts[rel_path] = line_numbers
                except Exception as e:
                    print("\nError reading {}: {}".format(file_path, str(e)))
    
    return hardcoded_scripts

def categorize_scripts(scripts):
    """Categorize scripts by their type based on path.
    
    Args:
        scripts (dict): Dictionary of script paths and their line numbers
        
    Returns:
        dict: Dictionary of categorized scripts with line numbers
    """
    categories = {
        'DarkSide': {},
        'Rhino Apps': {},
        'Revit Apps': {},
        'Library Files': {}
    }
    
    for script, line_numbers in scripts.items():
        if script.startswith('DarkSide/'):
            categories['DarkSide'][script] = line_numbers
        elif '_rhino/' in script:
            categories['Rhino Apps'][script] = line_numbers
        elif '_revit/' in script:
            categories['Revit Apps'][script] = line_numbers
        else:
            categories['Library Files'][script] = line_numbers
    
    # Sort scripts within each category
    for category in categories:
        categories[category] = dict(sorted(categories[category].items()))
    
    return categories

def update_self():
    """Update the JSON file with the latest list of scripts containing hardcoded paths."""
    new_scripts = scan_repo_for_hardcoded_paths()
    categorized_scripts = categorize_scripts(new_scripts)
    save_hardcoded_paths(categorized_scripts)
    print("\nUpdated hardcoded paths list in {}".format(get_json_path()))
    
    # Print summary of findings
    total_occurrences = sum(len(lines) for scripts in categorized_scripts.values() for lines in scripts.values())
    print("\nFound {} occurrences of hardcoded paths in {} files:".format(
        total_occurrences,
        sum(len(scripts) for scripts in categorized_scripts.values())
    ))
    for category, scripts in categorized_scripts.items():
        if scripts:
            print("\n{}:".format(category))
            for script, lines in scripts.items():
                print("  {} (lines: {})".format(script, ", ".join(map(str, lines))))

if __name__ == "__main__":
    update_self()
