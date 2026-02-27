# Slow Uploader for Raspberry Pi
A Python script for safely uploading large batches of images and videos to a homeserver (e.g., Immich) running on a Raspberry Pi, throttling the upload rate to avoid overheating or crashing.

## Features
Supports JPEG, PNG, TIFF image metadata extraction using EXIF

Extracts metadata from common video formats via pymediainfo

Automatically throttles upload frequency (default: every 30 seconds)

Skips previously uploaded files using a file-number threshold

Designed for use with servers like Immich that accept HTTP POST uploads with API keys

## Why?
Raspberry Pi devices can easily overheat or crash when handling too many uploads at once. This script spaces out uploads at configurable intervals to prevent that, ensuring your media makes it to the server safely and slowly.

## Requirements
 - Python 3.8+
 - Required Python Packages:
    - pip install pillow pymediainfo python-dotenv requests

## Env Setup
Create a .env file in the root of the project with the following
```
API_KEY=your_immich_api_key
BASE_URL=http://your-server-address/api
DIRECTORY_PATH=/path/to/directory
```

## Usage
Update CONTINUE_FILE_NUMBER and SLEEP_TIME variables at the top of the script as needed

Run the script
`python main.py`