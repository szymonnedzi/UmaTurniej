# UmaTurniej

Screenshot processing tool for Uma Musume Tournament - subdivides race screenshots into individual entry snippets and extracts race result data using OCR. **The processed results are returned as a `.txt` file** for easy sharing and analysis.

## Features

- **Unified workflow**: Process screenshots and extract data with a single command
- **Flask API**: Upload screenshots via REST API and get extraction results instantly
- Loads race screenshots (JPG/PNG) from the project root
- Extracts 7 individual race entry snippets per screenshot
- Saves snippets to `/screenshots/cropped/` for later inspection
- **OCR extraction**: Extracts position, character name, and player name from cropped snippets
- **Outputs race results to a `.txt` file** (`race_results.txt`) with formatted table layout
- Error handling and validation throughout the processing pipeline
- Docker support for easy deployment

## Installation

### Option 1: Using Docker (Recommended)

Docker provides a containerized environment with all dependencies pre-installed.

**Prerequisites**: Docker must be installed on your system.

```bash
# Build the Docker image
docker build -t umaturniej .

# Or use Docker Compose (recommended)
docker compose build
```

### Option 2: Local Installation

```bash
pip install -r requirements.txt
```

**Note**: Tesseract OCR must be installed on your system:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## Usage

### Option 1: Unified Workflow (Recommended for Local Processing)

This is the easiest way to process screenshots and receive the results as a text file:

#### With Local Installation

1. Place race screenshots (JPG/PNG) in the project root directory
2. Run the main script to process everything:
   ```bash
   python main.py
   ```
3. **The processed table will be saved to `race_results.txt`** in the project root
4. The script will clearly display the location of the output file upon completion

#### With Docker

```bash
# Using Docker Compose
docker compose run --rm umaturniej python main.py

# Or using Docker CLI
docker run --rm -v $(pwd):/app umaturniej python main.py
```

### Option 2: Flask API (Recommended for Docker)

The Flask API provides a simple REST endpoint to upload screenshots and get extraction results.

1. Start the API server:
   ```bash
   python main.py api
   # Or directly:
   python app.py
   ```

2. The API will be available at `http://localhost:5000`

3. Upload a screenshot using curl:
   ```bash
   curl -X POST -F "file=@your_screenshot.jpg" http://localhost:5000/api/upload
   ```

4. Or use any HTTP client to POST to `/api/upload` with multipart/form-data

**API Endpoints:**
- `GET /` - API information and available endpoints
- `GET /api/health` - Health check
- `POST /api/upload` - Upload screenshot and get extraction results
  - Accepts: `multipart/form-data` with `file` field
  - Returns: JSON with extracted race data

### Option 3: Manual Step-by-Step Processing

Alternatively, you can run each step separately:

#### Using Docker

**With Docker Compose (recommended)**

1. Place race screenshots in the project root directory
2. Extract snippets from screenshots:
   ```bash
   docker compose run --rm umaturniej python screenshot_processing/process_screenshots.py
   ```
3. Extract race data using OCR:
   ```bash
   docker compose run --rm umaturniej python ocr_extraction/extract_ocr_data.py
   ```
4. Results will be saved to `race_results.txt` and snippets to `screenshots/cropped/`

**With Docker CLI**

1. Place race screenshots in the project root directory
2. Run the processing script:
   ```bash
   docker run --rm -v $(pwd):/app umaturniej python screenshot_processing/process_screenshots.py
   ```
3. Run the OCR extraction script:
   ```bash
   docker run --rm -v $(pwd):/app umaturniej python ocr_extraction/extract_ocr_data.py
   ```
4. Results will be saved to `race_results.txt` and snippets to `screenshots/cropped/`

#### Using Local Installation

**Step 1: Extract Snippets from Screenshots**

1. Place race screenshots in the project root directory
2. Run the processing script:
   ```bash
   python screenshot_processing/process_screenshots.py
   ```
3. Extracted snippets will be saved to `screenshots/cropped/`

**Step 2: Extract Race Data using OCR**

1. Ensure cropped snippets exist in `screenshots/cropped/`
2. Run the OCR extraction script:
   ```bash
   python ocr_extraction/extract_ocr_data.py
   ```
3. Results will be saved to `race_results.txt`

## Directory Structure

```
UmaTurniej/
├── app.py                     # Flask API application
├── main.py                    # Main entry point (unified workflow or API launcher)
├── *.jpg                      # Place your race screenshots here for processing
├── test/
│   └── test_input/            # Starter test screenshots (sample data)
│       └── *.jpg              # Example race screenshots for testing
├── race_results.txt           # OCR-extracted race results (OUTPUT)
├── screenshots/
│   ├── uploads/               # API uploaded screenshots
│   └── cropped/               # Extracted entry snippets (intermediate)
├── screenshot_processing/
│   └── process_screenshots.py # Snippet extraction script (can run standalone)
├── ocr_extraction/
│   └── extract_ocr_data.py    # OCR data extraction script (can run standalone)
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Docker Compose service definition
├── .dockerignore              # Files to exclude from Docker image
├── requirements.txt           # Python dependencies
└── README.md
```

## Output

### Processed Table (race_results.txt)
After processing, you will receive a **`race_results.txt` file** containing the extracted race data in a formatted table:
```
UmaTurniej Race Results - OCR Extraction
==================================================

Screenshot: {screenshot_name}
----------------------------------------
  1st: {character_name} - {player_name}
  2nd: {character_name} - {player_name}
  ...

==================================================
Total entries processed: {count}
```

### Intermediate Files

#### Snippet Extraction
Each source screenshot produces 7 individual entry snippet images in `screenshots/cropped/`:
- `{screenshot_name}_entry_1.png`
- `{screenshot_name}_entry_2.png`
- ...
- `{screenshot_name}_entry_7.png`

**Note**: OCR extraction is best-effort and may have inaccuracies depending on image quality.

## Docker

When running in a Docker container, the Flask API is the recommended approach:

```dockerfile
# Example Dockerfile usage
FROM python:3.12-slim

# Install Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask API
CMD ["python", "app.py"]
```

Then build and run:
```bash
docker build -t umaturniej .
docker run -p 5000:5000 umaturniej
```
