"""
XMP Metadata Merger

A script to merge XMP sidecar files into their corresponding media files (images and videos).

Long Description:
----------------
This script processes media files and their corresponding XMP sidecar files, merging the
metadata from the XMP files into the media files. It supports both image and video files,
can process subdirectories recursively, and saves the processed files to a specified
output directory while preserving the original files.

Features:
---------
- Processes both image and video files
- Handles subdirectories recursively
- Preserves original files by saving processed versions to a separate directory
- Automatically handles filename conflicts in the output directory
- Supports custom output directory naming
- Detailed processing feedback and summary statistics

Supported Media Formats:
----------------------
Images: .jpg, .jpeg, .png, .tiff, .cr2, .nef, .arw, .dng, .heic
Videos: .mp4, .mov, .avi, .mkv, .mts, .m2ts

Dependencies:
------------
- Python 3.6+
- exiftool (must be installed and available in system PATH)

Usage:
------
Basic usage:
    python3 script.py

With options:
    python3 script.py -d /path/to/files -o "Output Folder"
    python3 script.py --no-recursive
    python3 script.py --quiet

Command line options:
    -d, --directory: Input directory (default: current directory)
    -o, --output-dir: Output directory name (default: "Processed Media")
    --no-recursive: Don't process subdirectories
    -q, --quiet: Reduce output verbosity
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, List, Dict

def get_unique_filename(target_path: Path) -> Path:
    """
    Generate a unique filename by appending a number if the file already exists.
    
    Args:
        target_path (Path): The desired file path
    
    Returns:
        Path: A unique file path
    """
    if not target_path.exists():
        return target_path
    
    counter = 1
    while True:
        # Get the stem (filename without extension) and suffix
        stem = target_path.stem
        suffix = target_path.suffix
        
        # Create new filename with counter
        new_path = target_path.with_name(f"{stem}_{counter}{suffix}")
        
        if not new_path.exists():
            return new_path
        counter += 1

def ensure_output_dir(base_dir: str, output_dirname: str = "Processed Media") -> Path:
    """
    Create and return the output directory path.
    
    Args:
        base_dir (str): Base directory where the output folder should be created
        output_dirname (str): Name of the output directory
    
    Returns:
        Path: Path to the output directory
    """
    output_dir = Path(base_dir) / output_dirname
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_media_files(directory: str, recursive: bool = True) -> Tuple[List[Path], List[Path]]:
    """
    Get lists of media files and XMP files from the directory and optionally its subdirectories.
    
    Args:
        directory (str): Path to the directory containing media files and XMP files
        recursive (bool): Whether to search in subdirectories
    
    Returns:
        Tuple containing lists of media files and XMP files
    """
    dir_path = Path(directory)
    
    # Common media file extensions
    media_extensions = (
        # Images
        '.jpg', '.jpeg', '.png', '.tiff', '.cr2', '.nef', '.arw', '.dng', '.heic',
        # Videos
        '.mp4', '.mov', '.avi', '.mkv', '.mts', '.m2ts'
    )
    
    # Get all media and XMP files
    media_files = []
    xmp_files = []
    
    if recursive:
        # Walk through all subdirectories
        for root, _, files in os.walk(dir_path):
            root_path = Path(root)
            media_files.extend([
                root_path / f for f in files 
                if Path(f).suffix.lower() in media_extensions
            ])
            xmp_files.extend([
                root_path / f for f in files 
                if f.lower().endswith('.xmp')
            ])
    else:
        # Only search in the current directory
        media_files = [
            f for f in dir_path.glob('*') 
            if f.suffix.lower() in media_extensions
        ]
        xmp_files = list(dir_path.glob('*.xmp'))
    
    return media_files, xmp_files

def organize_xmp_files(xmp_files: List[Path]) -> Dict[str, Path]:
    """
    Organize XMP files into a dictionary, handling both standard and video XMP naming.
    
    Args:
        xmp_files (List[Path]): List of XMP file paths
    
    Returns:
        Dictionary mapping base filenames to XMP paths
    """
    xmp_dict = {}
    for xmp in xmp_files:
        # Handle XMP files that include the full filename (e.g., "image.jpg.xmp")
        base_name = xmp.name.replace('.xmp', '')
        xmp_dict[base_name] = xmp
    return xmp_dict

def merge_xmp_metadata(directory: str, output_dirname: str = "Processed Media", recursive: bool = True, verbose: bool = True) -> None:
    """
    Merge XMP sidecar files into their corresponding media files in the given directory.
    
    Args:
        directory (str): Path to the directory containing media files and XMP files
        output_dirname (str): Name of the output directory
        recursive (bool): Whether to process subdirectories
        verbose (bool): Whether to print detailed progress information
    """
    print("\n=== Starting metadata merge process ===\n")
    
    # Create output directory
    output_dir = ensure_output_dir(directory, output_dirname)
    if verbose:
        print(f"Output directory: {output_dir}\n")
    
    # Get lists of files
    media_files, xmp_files = get_media_files(directory, recursive)
    
    if verbose:
        print(f"Found {len(media_files)} media files")
        print(f"Found {len(xmp_files)} XMP files\n")
    
    # Create a dictionary of XMP files keyed by their complete filename
    xmp_dict = organize_xmp_files(xmp_files)
    
    # Track statistics
    processed = 0
    skipped = 0
    errors = 0
    
    for media_file in media_files:
        if verbose:
            print(f"Processing file: {media_file.relative_to(directory)}")
        
        # Check if there's a corresponding XMP file using the full filename
        if media_file.name not in xmp_dict:
            if verbose:
                print(f"⚠️  No XMP file found for {media_file.name}, skipping...")
            skipped += 1
            continue
        
        xmp_file = xmp_dict[media_file.name]
        
        # Create a temporary copy of the media file
        temp_file = get_unique_filename(output_dir / media_file.name)
        try:
            # Copy the original file to the output directory
            shutil.copy2(media_file, temp_file)
            
            # Use exiftool to copy metadata from XMP to the copied media file
            cmd = [
                'exiftool',
                '-tagsfromfile',
                str(xmp_file),
                '-all:all',
                '-overwrite_original',
                str(temp_file)
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            if verbose:
                print(f"✅ Successfully processed and saved to: {temp_file.name}")
            processed += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error processing {media_file.name}:")
            print(f"   {e.stderr.strip()}")
            # Clean up failed file if it exists
            if temp_file.exists():
                temp_file.unlink()
            errors += 1
            
        except Exception as e:
            print(f"❌ Unexpected error processing {media_file.name}:")
            print(f"   {str(e)}")
            # Clean up failed file if it exists
            if temp_file.exists():
                temp_file.unlink()
            errors += 1
        
        if verbose:
            print()  # Add blank line between files for readability
    
    # Print summary
    print("\n=== Process Summary ===")
    print(f"Total media files found: {len(media_files)}")
    print(f"Successfully processed: {processed}")
    print(f"Skipped (no XMP): {skipped}")
    print(f"Errors: {errors}")
    print(f"\nProcessed files saved to: {output_dir}")
    print("\nProcess completed!")

if __name__ == '__main__':
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Merge XMP metadata into media files')
    parser.add_argument('--directory', '-d', type=str, default=os.getcwd(),
                        help='Directory to process (default: current directory)')
    parser.add_argument('--no-recursive', action='store_true',
                        help='Do not process subdirectories')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Reduce output verbosity')
    parser.add_argument('--output-dir', '-o', type=str, default="Processed Media",
                        help='Name of output directory (default: "Processed Media")')
    
    args = parser.parse_args()
    
    try:
        # Check if exiftool is installed
        subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ExifTool is not installed or not found in PATH")
        print("Please install ExifTool before running this script")
        exit(1)
    
    merge_xmp_metadata(
        directory=args.directory,
        output_dirname=args.output_dir,
        recursive=not args.no_recursive,
        verbose=not args.quiet
    )