#!/usr/bin/env python3
"""
Screenshot Processing Script for UmaTurniej
Subdivides race screenshots into smaller image snippets for later OCR processing.

This script:
1. Loads all image files (JPG/PNG) from the project root directory
2. For each screenshot, extracts 7 individual race entry snippets
3. Saves the snippets to the /screenshots/cropped directory

The script uses OCR-based anchor detection to dynamically determine entry positions,
falling back to fixed pixel values if anchor text is not found.
"""

import warnings
from pathlib import Path

import pytesseract
from PIL import Image

# Race entry region coordinates (for 1716x965 resolution screenshots)
# These are default/fallback values used when OCR-based detection fails
ENTRY_LEFT = 215       # Left edge of entry boxes
ENTRY_RIGHT = 625      # Right edge of entry boxes
ENTRY_START_Y = 68     # Y position of first entry (fallback)
ENTRY_HEIGHT = 105     # Height of each entry box
ENTRY_GAP = 3          # Gap between entries
NUM_ENTRIES = 7        # Number of visible entries per screenshot

# OCR anchor configuration
# The anchor text is detected in the header region and used to calculate
# the starting Y position for entry extraction
ANCHOR_TEXT = "Select"              # Text to search for as anchor
ANCHOR_SEARCH_REGION = (100, 0, 400, 80)  # Region to search for anchor (left, top, right, bottom)
ANCHOR_TO_ENTRY_OFFSET = 43         # Pixels from anchor bottom to first entry top


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def detect_anchor_position(img: Image.Image) -> int | None:
    """
    Detect the anchor text position using OCR to dynamically determine
    the starting Y coordinate for entry extraction.

    Searches for ANCHOR_TEXT within ANCHOR_SEARCH_REGION and returns the
    Y coordinate of the bottom of the anchor text.

    Args:
        img: PIL Image object of the screenshot

    Returns:
        Y coordinate of anchor text bottom, or None if not found
    """
    # Crop to the anchor search region
    search_region = img.crop(ANCHOR_SEARCH_REGION)

    # Run OCR with bounding box data
    # Use PSM 6 (assume a single uniform block of text) for better detection of UI text
    data = pytesseract.image_to_data(
        search_region, output_type=pytesseract.Output.DICT, config='--psm 6'
    )

    # Search for the anchor text
    for i, text in enumerate(data['text']):
        # Use case-insensitive matching to handle OCR variations
        if text.strip().lower() == ANCHOR_TEXT.lower():
            # Calculate the bottom Y position of the anchor in original image coordinates
            # Add the search region's top offset to convert to original image coordinates
            anchor_top = data['top'][i] + ANCHOR_SEARCH_REGION[1]
            anchor_height = data['height'][i]
            anchor_bottom = anchor_top + anchor_height
            return anchor_bottom

    return None


def load_screenshots(project_root: Path) -> list[Path]:
    """
    Load all image files (PNG and JPG) from the project root directory.

    Args:
        project_root: Path to the project root directory

    Returns:
        List of paths to image files
    """
    image_files = []
    for pattern in ["*.png", "*.jpg", "*.jpeg"]:
        image_files.extend(project_root.glob(pattern))
    # Exclude any files in subdirectories
    image_files = [f for f in image_files if f.parent == project_root]
    return sorted(image_files)


def extract_entry_snippets(image_path: Path, output_dir: Path) -> list[Path]:
    """
    Extract individual race entry snippets from a screenshot.

    Uses OCR-based anchor detection to dynamically determine the starting
    Y position for entries. Falls back to fixed ENTRY_START_Y if anchor
    text is not detected.

    Args:
        image_path: Path to the source screenshot
        output_dir: Directory to save the extracted snippets

    Returns:
        List of paths to the extracted snippet images
    """
    img = Image.open(image_path)
    width, height = img.size

    # Attempt OCR-based anchor detection for dynamic Y positioning
    anchor_bottom = detect_anchor_position(img)

    if anchor_bottom is not None:
        # Calculate entry start Y from detected anchor position
        start_y = anchor_bottom + ANCHOR_TO_ENTRY_OFFSET
        print(f"  OCR anchor detected at y={anchor_bottom}, entries start at y={start_y}")
    else:
        # Fallback to fixed value with warning
        warnings.warn(
            f"OCR anchor '{ANCHOR_TEXT}' not found in {image_path.name}; "
            "using fixed ENTRY_START_Y value",
            UserWarning,
            stacklevel=2
        )
        print(f"  Warning: OCR anchor not found, using fallback y={ENTRY_START_Y}")
        start_y = ENTRY_START_Y

    # Scale coordinates if image size differs from expected
    if width != 1716 or height != 965:
        print(f"  Warning: Image size {width}x{height} differs from expected 1716x965")
        scale_x = width / 1716
        scale_y = height / 965
        left = int(ENTRY_LEFT * scale_x)
        right = int(ENTRY_RIGHT * scale_x)
        # Scale the OCR-detected or fallback start_y
        start_y = int(start_y * scale_y)
        entry_height = int(ENTRY_HEIGHT * scale_y)
        entry_gap = int(ENTRY_GAP * scale_y)
    else:
        left = ENTRY_LEFT
        right = ENTRY_RIGHT
        entry_height = ENTRY_HEIGHT
        entry_gap = ENTRY_GAP

    extracted_paths = []

    for i in range(NUM_ENTRIES):
        top = start_y + i * (entry_height + entry_gap)
        bottom = top + entry_height

        if bottom > height:
            break

        entry_box = (left, top, right, bottom)
        entry_img = img.crop(entry_box)

        output_filename = f"{image_path.stem}_entry_{i + 1}.png"
        output_path = output_dir / output_filename
        entry_img.save(output_path, "PNG")
        extracted_paths.append(output_path)

    return extracted_paths


def main() -> None:
    """Main entry point for the screenshot processing script."""
    project_root = get_project_root()
    output_dir = project_root / "screenshots" / "cropped"

    output_dir.mkdir(parents=True, exist_ok=True)

    print("UmaTurniej Screenshot Snippet Extractor")
    print("=" * 45)

    screenshots = load_screenshots(project_root)

    if not screenshots:
        print(f"No image files found in {project_root}")
        return

    print(f"Found {len(screenshots)} screenshot(s) to process")

    total_snippets = 0

    for screenshot in screenshots:
        print(f"\nProcessing: {screenshot.name}")

        try:
            snippet_paths = extract_entry_snippets(screenshot, output_dir)
            print(f"  - Extracted {len(snippet_paths)} snippet(s)")

            for path in snippet_paths:
                print(f"    - {path.name}")

            total_snippets += len(snippet_paths)

        except (ValueError, OSError) as e:
            print(f"  - Error processing {screenshot.name}: {e}")

    print("\n" + "=" * 45)
    print(f"COMPLETE: Extracted {total_snippets} total snippets")
    print(f"Snippets saved to: {output_dir}")


if __name__ == "__main__":
    main()
