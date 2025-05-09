import os
import zipfile
import shutil
from pathlib import Path
import psutil
import re
from collections import defaultdict
import sys

# Source and destination paths
SOURCE_DRIVE = r"E:\drive"
TEMP_WORKING_DIR = r"C:\Users\szhang\Desktop\g drive expander"
TARGET_SUBFOLDER = "19 job hunt"
ERROR_LOG = os.path.join(TEMP_WORKING_DIR, "extract_errors.log")

def get_disk_space(path):
    """Get available disk space for the given path"""
    partition = psutil.disk_usage(path)
    return {
        'total': partition.total,
        'used': partition.used,
        'free': partition.free
    }

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return "{:.2f} {}".format(size_bytes, unit)
        size_bytes /= 1024.0

def ensure_working_dir():
    """Ensure the temporary working directory exists and has enough space"""
    Path(TEMP_WORKING_DIR).mkdir(parents=True, exist_ok=True)
    
    # Check available space
    space_info = get_disk_space(TEMP_WORKING_DIR)
    print("\nDisk space information for working directory:")
    print("Total space: {}".format(format_size(space_info['total'])))
    print("Used space: {}".format(format_size(space_info['used'])))
    print("Free space: {}".format(format_size(space_info['free'])))
    
    return space_info['free']

def identify_takeout_batch(zip_files):
    """Group zip files into their respective takeout batches"""
    takeout_pattern = re.compile(r'(takeout-\d{8}T\d{6}Z)-(\d{3})\.zip')
    
    batches = defaultdict(list)
    other_files = []
    
    for file_path in zip_files:
        filename = os.path.basename(file_path)
        match = takeout_pattern.match(filename)
        
        if match:
            batch_id = match.group(1)
            part_number = int(match.group(2))
            batches[batch_id].append((file_path, part_number))
        else:
            other_files.append(file_path)
    
    # Sort each batch by part number
    for batch_id in batches:
        batches[batch_id].sort(key=lambda x: x[1])
    
    return batches, other_files

def get_folder_structure(zip_path):
    """Get the folder structure from a zip file"""
    folders = set()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                dir_path = os.path.dirname(file_info.filename)
                if dir_path:
                    folders.add(dir_path)
    except zipfile.BadZipFile:
        print("Error: {} is not a valid zip file".format(zip_path))
    return sorted(list(folders))

def check_missing_parts(files):
    """Check for missing part numbers in a batch and return a list of missing parts"""
    part_numbers = [part_num for _, part_num in files]
    if not part_numbers:
        return []
    min_part = min(part_numbers)
    max_part = max(part_numbers)
    missing = [num for num in range(min_part, max_part + 1) if num not in part_numbers]
    return missing

def analyze_batch(batch_id, files):
    """Analyze a complete batch of takeout files"""
    print("\n" + "="*80)
    print("Batch: {}".format(batch_id))
    print("Number of parts: {}".format(len(files)))
    print("="*80)
    
    # Check for missing parts
    missing = check_missing_parts(files)
    if missing:
        print("WARNING: Missing part numbers: {}".format(", ".join("{:03d}".format(m) for m in missing)))
    else:
        print("All parts are present and accounted for!")
    
    # Get structure from first file
    first_file = files[0][0]
    folders = get_folder_structure(first_file)
    
    print("\nFolder Structure:")
    for folder in folders:
        print("  - {}".format(folder))
    
    print("\nFiles in this batch:")
    for file_path, part_num in files:
        print("  - Part {}: {}".format(part_num, os.path.basename(file_path)))

def extract_target_subfolder_flat(files, extract_to, target_subfolder):
    """Extract only the target subfolder from all zip parts directly into extract_to, cutting off parent folders. Shows progress."""
    extracted_files = 0
    errors = []
    # First, count total files to extract for progress
    print("Scanning for files to extract...")
    to_extract = []
    for zip_path, part_num in files:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    lower_path = file_info.filename.lower()
                    target_index = lower_path.find(target_subfolder.lower())
                    if target_index != -1 and not file_info.is_dir():
                        to_extract.append((zip_path, part_num, file_info, file_info.filename[target_index:]))
        except zipfile.BadZipFile:
            errors.append("{}: Bad zip file".format(zip_path))
    total = len(to_extract)
    print("Found {} files to extract containing '{}'".format(total, target_subfolder))
    if total == 0:
        print("Nothing to extract!")
        return
    # Extraction with progress
    for idx, (zip_path, part_num, file_info, relative_path) in enumerate(to_extract, 1):
        target_path = os.path.join(extract_to, relative_path)
        target_folder = os.path.dirname(target_path)
        Path(target_folder).mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
            extracted_files += 1
        except Exception as e:
            errors.append("{}: {}".format(target_path, str(e)))
        # Print progress
        percent = (idx / total) * 100
        sys.stdout.write("\rExtracting: {}/{} ({:.2f}%)".format(idx, total, percent))
        sys.stdout.flush()
    print("\nExtraction complete! Extracted {} files/folders containing '{}' to {}".format(extracted_files, target_subfolder, extract_to))
    if errors:
        print("Some files could not be extracted. See error log at {}".format(ERROR_LOG))
        with open(ERROR_LOG, 'w', encoding='utf-8') as log:
            for err in errors:
                log.write(err + "\n")

def main():
    # Check available space
    free_space = ensure_working_dir()
    
    # Get all zip files
    zip_files = []
    for root, _, files in os.walk(SOURCE_DRIVE):
        for file in files:
            if file.endswith('.zip'):
                file_path = os.path.join(root, file)
                zip_files.append(file_path)
    
    # Group files into takeout batches
    batches, other_files = identify_takeout_batch(zip_files)
    
    print("\nFound {} takeout batches and {} other zip files".format(
        len(batches), len(other_files)))
    
    # Analyze each batch
    total_required_space = 0
    for batch_id, files in batches.items():
        analyze_batch(batch_id, files)
        total_required_space += len(files)
        print("\nNow extracting only '{}' from batch {}...".format(TARGET_SUBFOLDER, batch_id))
        extract_target_subfolder_flat(files, TEMP_WORKING_DIR, TARGET_SUBFOLDER)
    
    # Check if we have enough space
    if total_required_space > free_space:
        print("\nWARNING: Not enough disk space!")
        print("Required space: {}".format(format_size(total_required_space)))
        print("Available space: {}".format(format_size(free_space)))
        print("Additional space needed: {}".format(format_size(total_required_space - free_space)))
        return
    
    if other_files:
        print("\n" + "="*80)
        print("Other zip files (not part of takeout batches):")
        print("="*80)
        for file_path in other_files:
            print("  - {}".format(file_path))
            folders = get_folder_structure(file_path)
            if folders:
                print("    Folders:")
                for folder in folders:
                    print("      - {}".format(folder))

if __name__ == "__main__":
    main()