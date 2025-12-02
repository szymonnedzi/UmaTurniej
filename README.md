# UmaTurniej

Screenshot processing tool for Uma Musume Tournament - subdivides race screenshots into individual entry snippets and extracts race result data using OCR. **The processed results are returned as a `.txt` file** for easy sharing and analysis.

## Features

- **Unified workflow**: Process screenshots and extract data with a single command
- Loads race screenshots (JPG/PNG) from the project root
- Extracts 7 individual race entry snippets per screenshot
- Saves snippets to `/screenshots/cropped/` for later inspection
- **OCR extraction**: Extracts position, character name, and player name from cropped snippets
- **Outputs race results to a `.txt` file** (`race_results.txt`) with formatted table layout
- Error handling and validation throughout the processing pipeline

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

### Quick Start (Recommended)

This is the easiest way to process screenshots and receive the results as a text file:

1. Place race screenshots (JPG/PNG) in the project root directory
2. Run the main script to process everything:
   ```bash
   python main.py
   ```
3. **The processed table will be saved to `race_results.txt`** in the project root
4. The script will clearly display the location of the output file upon completion

### Manual Step-by-Step Processing

Alternatively, you can run each step separately:

#### Step 1: Extract Snippets from Screenshots

1. Place race screenshots in the project root directory
2. Run the processing script:
   ```bash
   python scripts/process_screenshots.py
   ```
3. Extracted snippets will be saved to `screenshots/cropped/`

#### Step 2: Extract Race Data using OCR

1. Ensure cropped snippets exist in `screenshots/cropped/`
2. Run the OCR extraction script:
   ```bash
   python scripts/extract_ocr_data.py
   ```
3. Results will be saved to `race_results.txt`

## Directory Structure

```
UmaTurniej/
├── main.py                    # Main entry point (unified workflow)
├── *.jpg                      # Source race screenshots
├── race_results.txt           # OCR-extracted race results (OUTPUT)
├── screenshots/
│   └── cropped/               # Extracted entry snippets (intermediate)
├── scripts/
│   ├── process_screenshots.py # Snippet extraction script (can run standalone)
│   └── extract_ocr_data.py    # OCR data extraction script (can run standalone)
├── requirements.txt
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