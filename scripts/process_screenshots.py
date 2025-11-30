#!/usr/bin/env python3
"""
Screenshot Processing Script for UmaTurniej
Subdivides race screenshots into smaller image snippets for later OCR processing.

This script:
1. Loads all image files (JPG/PNG) from the project root directory
2. For each screenshot, extracts 7 individual race entry snippets
3. Saves the snippets to the /screenshots/cropped directory
"""

from pathlib import Path

from PIL import Image

# Race entry region coordinates (for 1716x965 resolution screenshots)
ENTRY_LEFT = 215       # Left edge of entry boxes
ENTRY_RIGHT = 625      # Right edge of entry boxes
ENTRY_START_Y = 68     # Y position of first entry
ENTRY_HEIGHT = 105     # Height of each entry box
ENTRY_GAP = 3          # Gap between entries
NUM_ENTRIES = 7        # Number of visible entries per screenshot


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


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

    Args:
        image_path: Path to the source screenshot
        output_dir: Directory to save the extracted snippets

    Returns:
        List of paths to the extracted snippet images
    """
    img = Image.open(image_path)
    width, height = img.size

    # Scale coordinates if image size differs from expected
    if width != 1716 or height != 965:
        print(f"  Warning: Image size {width}x{height} differs from expected 1716x965")
        scale_x = width / 1716
        scale_y = height / 965
        left = int(ENTRY_LEFT * scale_x)
        right = int(ENTRY_RIGHT * scale_x)
        start_y = int(ENTRY_START_Y * scale_y)
        entry_height = int(ENTRY_HEIGHT * scale_y)
        entry_gap = int(ENTRY_GAP * scale_y)
    else:
        left = ENTRY_LEFT
        right = ENTRY_RIGHT
        start_y = ENTRY_START_Y
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
