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
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Processing Screenshots

1. Place your race screenshots (PNG format) in the `/screenshots` directory
2. Run the processing script:
   ```bash
   python scripts/process_screenshots.py
   ```
3. Results will be saved to `screenshots/race_results.txt`
4. Cropped images are saved to `screenshots/cropped/`

## Directory Structure

```
UmaTurniej/
├── screenshots/
│   ├── cropped/           # Cropped images (left half only)
│   └── race_results.txt   # Extracted race results
├── scripts/
│   └── process_screenshots.py  # Main processing script
├── requirements.txt
└── README.md
```

## Output Format

The output file contains race results in the following format:

```
Race: screenshot1.png
----------------------------------------
1st: CharacterName - UserName
2nd: CharacterName - UserName
3rd: CharacterName - UserName
...
```

## Notes

- Screenshots should have race standings visible on the left half of the image
- The script crops the right half and processes only the left portion
- OCR accuracy depends on image quality and text clarity