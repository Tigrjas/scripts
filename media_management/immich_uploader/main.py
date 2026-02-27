from datetime import datetime
from typing import Tuple
from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
from pymediainfo import MediaInfo
from dotenv import load_dotenv
import time
import requests
import os
import re

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
DIRECTORY_PATH = os.getenv("DIRECTORY_PATH")
SLEEP_TIME = 30 
CONTINUE_FILE_NUMBER = 0


def get_metadata(file_path: Path):
    """
    Extracts metadata from image or video files.

    Args:
        file_path (Path): A Path object pointing to the file.

    Returns:
        dict: Metadata dictionary, or None if unsupported or failed.
    """
    ext = file_path.suffix.lower()

    if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
        try:
            image = Image.open(file_path)
            exif_data = image.getexif()
            if exif_data:
                return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            else:
                return {}
        except Exception as e:
            print(f"Failed to read image metadata: {e}")
            return None

    elif ext in ['.mov', '.mp4', '.avi', '.mkv']:
        try:
            media_info = MediaInfo.parse(file_path)
            metadata = {}
            for track in media_info.tracks:
                if track.track_type == "General":
                    metadata.update({
                        "duration": track.duration,
                        "file_size": track.file_size,
                        "format": track.format,
                        "creation_date": track.tagged_date,
                        "title": track.title
                    })
            return metadata
        except Exception as e:
            print(f"Failed to read video metadata: {e}")
            return None

    else:
        print(f"Unsupported file type: {ext}")
        return None

def process_images(directory_path: str):
    """
    Access a directory with the provided path and processes the images/videos in that directory.

    Args:
        directory_path (str): A string of the directory path 

    Returns:
        None: It just prints out if each image is successful or not
    """
    directory = Path(directory_path).iterdir()
    count = 0
    failure_count = 0
    start_time = time.perf_counter()
    
    for file in directory:
        file_number = extract_number_from_filename(str(file))
        if file_number is None:
            continue
        if file_number >= CONTINUE_FILE_NUMBER:
            failure_count += upload(str(file))
            count += 1
            time.sleep(SLEEP_TIME)
        
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    print(f"""Processing of Images completed
    Elapsed time: {formatted_time}
    Count: {count}
    Failed: {failure_count}
    """)


def extract_number_from_filename(file_path: str):
    """
    Gets the number from the base of the file name

    Args:
        file_path (str): A string of the absolute file path

    Returns
        int: The integer part of the file name as an int
    """
    pattern = r'IMG_(\d+)'
    match = re.search(pattern, file_path)
    if match:
        return int(match.group(1))
    else:
        return None

def upload(file: str):
    """
    Uploads image to Immich
  
    Args:
      file (str): The file name as a string

    Returns:
      None: It just prints the json response
    """

    print(f"Uploading: {file}")

    stats = os.stat(file)
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    
    data = {
        'device'
    }

    data = {
        'deviceAssetId': f'{file}-{stats.st_mtime}',
        'deviceId': 'python',
        'fileCreatedAt': datetime.fromtimestamp(stats.st_mtime),
        'fileModifiedAt': datetime.fromtimestamp(stats.st_mtime),
        'isFavorite': 'false',
    }

    files = {
        'assetData': open(file, 'rb')
    }

    response = requests.post(
        f'{BASE_URL}/assets', headers=headers, data=data, files=files)
    
    status = response.json()['status']

    if status == 'created':
        print(f"Success: {status}")
        return 0
    else:
        print(f"Failed: {status}")
        return 1

def main():
    print(f"Starting the processing of images/videos in the directory {DIRECTORY_PATH}")
    process_images(DIRECTORY_PATH)


if __name__ == "__main__":
    main()
    