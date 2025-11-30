# UmaTurniej

Screenshot Processing and OCR Application for Uma Musume Tournament race results.

## Features

- Loads PNG screenshots from the `/screenshots` directory
- Crops the right half of images (keeping left half with race standings)
- Uses OCR (pytesseract) to extract race positions, character names, and user names
- Outputs results to a formatted text file

## Installation

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Processing Screenshots

1. Place your race screenshots in the `/screenshots` directory
2. Run the processing script:
   ```bash
   python scripts/process_screenshots.py
   ```
3. Results will be saved to `screenshots/race_results.txt`
4. Cropped images are saved to `screenshots/cropped/`

### Generating Sample Screenshots (for testing)

```bash
python scripts/generate_sample_screenshots.py
```

## Directory Structure

```
UmaTurniej/
├── screenshots/
│   ├── cropped/           # Cropped images (left half only)
│   └── race_results.txt   # Extracted race results
├── scripts/
│   ├── process_screenshots.py      # Main processing script
│   └── generate_sample_screenshots.py  # Test image generator
├── requirements.txt
└── README.md
```

## Output Format

The output file contains race results in the following format:

```
Race: race1_screenshot.png
----------------------------------------
1st: Maruzensky - Kysix
2nd: Haru Urara - Sebaxd321
3rd: Oguri Cap - Archer
...
```