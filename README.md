# UmaTurniej

Screenshot processing tool for Uma Musume Tournament - subdivides race screenshots into individual entry snippets and extracts race result data using OCR.

## Features

- Loads race screenshots (JPG/PNG) from the project root
- Extracts 7 individual race entry snippets per screenshot
- Saves snippets to `/screenshots/cropped/` for later OCR processing
- **OCR extraction**: Extracts position, character name, and player name from cropped snippets
- Outputs race results to a text file (`race_results.txt`)

## Installation

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

### Step 1: Extract Snippets from Screenshots

1. Place race screenshots in the project root directory
2. Run the processing script:
   ```bash
   python scripts/process_screenshots.py
   ```
3. Extracted snippets will be saved to `screenshots/cropped/`

### Step 2: Extract Race Data using OCR

1. Ensure cropped snippets exist in `screenshots/cropped/`
2. Run the OCR extraction script:
   ```bash
   python scripts/extract_ocr_data.py
   ```
3. Results will be saved to `race_results.txt`

## Directory Structure

```
UmaTurniej/
├── *.jpg                      # Source race screenshots
├── race_results.txt           # OCR-extracted race results
├── screenshots/
│   └── cropped/               # Extracted entry snippets
├── scripts/
│   ├── process_screenshots.py # Snippet extraction script
│   └── extract_ocr_data.py    # OCR data extraction script
├── requirements.txt
└── README.md
```

## Output

### Snippet Extraction
Each source screenshot produces 7 individual entry snippet images:
- `{screenshot_name}_entry_1.png`
- `{screenshot_name}_entry_2.png`
- ...
- `{screenshot_name}_entry_7.png`

### OCR Extraction
The `race_results.txt` file contains extracted data in the format:
```
Screenshot: {screenshot_name}
----------------------------------------
  1st: {character_name} - {player_name}
  2nd: {character_name} - {player_name}
  ...
```

**Note**: OCR extraction is best-effort and may have inaccuracies depending on image quality.