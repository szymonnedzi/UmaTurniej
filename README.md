# UmaTurniej

Screenshot processing tool for Uma Musume Tournament - subdivides race screenshots into individual entry snippets.

## Features

- Loads race screenshots (JPG/PNG) from the project root
- Extracts 7 individual race entry snippets per screenshot
- Saves snippets to `/screenshots/cropped/` for later OCR processing

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place race screenshots in the project root directory
2. Run the processing script:
   ```bash
   python scripts/process_screenshots.py
   ```
3. Extracted snippets will be saved to `screenshots/cropped/`

## Directory Structure

```
UmaTurniej/
├── *.jpg                      # Source race screenshots
├── screenshots/
│   └── cropped/               # Extracted entry snippets
├── scripts/
│   └── process_screenshots.py # Main processing script
├── requirements.txt
└── README.md
```

## Output

Each source screenshot produces 7 individual entry snippet images:
- `{screenshot_name}_entry_1.png`
- `{screenshot_name}_entry_2.png`
- ...
- `{screenshot_name}_entry_7.png`