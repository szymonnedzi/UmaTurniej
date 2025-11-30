#!/usr/bin/env python3
"""
Screenshot Processing Script for UmaTurniej
Processes race screenshots to extract race standings using OCR.

This script:
1. Loads all .png images from the /screenshots directory
2. Crops off the right half (keeping only the left half with race standings)
3. Uses OCR (pytesseract) to extract placement, character name, and user name
4. Outputs results to screenshots/race_results.txt
"""

import re
import traceback
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

# OCR Configuration Constants
# oem=3: Default OCR Engine Mode (LSTM neural network)
# psm=6: Assume a single uniform block of text
OCR_CONFIG = r"--oem 3 --psm 6"

# Image preprocessing constants
DENOISE_FILTER_STRENGTH = 10
DENOISE_TEMPLATE_WINDOW_SIZE = 7
DENOISE_SEARCH_WINDOW_SIZE = 21
OCR_SCALE_FACTOR = 2


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_screenshots(screenshots_dir: Path) -> list[Path]:
    """
    Load all PNG images from the screenshots directory.

    Args:
        screenshots_dir: Path to the screenshots directory

    Returns:
        List of paths to PNG files
    """
    png_files = list(screenshots_dir.glob("*.png"))
    # Exclude cropped directory files
    png_files = [f for f in png_files if "cropped" not in str(f)]
    return sorted(png_files)


def crop_left_half(image_path: Path, output_dir: Path) -> Path:
    """
    Crop the right half off an image, keeping only the left half.

    Args:
        image_path: Path to the source image
        output_dir: Directory to save the cropped image

    Returns:
        Path to the cropped image
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    height, width = img.shape[:2]
    left_half = img[:, : width // 2]

    output_path = output_dir / f"{image_path.stem}_cropped.png"
    cv2.imwrite(str(output_path), left_half)
    return output_path


def preprocess_image_for_ocr(image_path: Path) -> np.ndarray:
    """
    Preprocess an image for better OCR results.

    Args:
        image_path: Path to the image

    Returns:
        Preprocessed image as numpy array
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(
        binary, None,
        DENOISE_FILTER_STRENGTH,
        DENOISE_TEMPLATE_WINDOW_SIZE,
        DENOISE_SEARCH_WINDOW_SIZE
    )

    # Scale up for better OCR
    scaled = cv2.resize(
        denoised, None, fx=OCR_SCALE_FACTOR, fy=OCR_SCALE_FACTOR,
        interpolation=cv2.INTER_CUBIC
    )

    return scaled


def extract_race_positions(image_path: Path) -> list[dict]:
    """
    Extract race positions from a cropped screenshot using OCR.

    Args:
        image_path: Path to the cropped image

    Returns:
        List of dictionaries with placement, character_name, and user_name
    """
    preprocessed = preprocess_image_for_ocr(image_path)

    # Convert to PIL Image for pytesseract
    pil_image = Image.fromarray(preprocessed)

    # Perform OCR with custom config for better results
    text = pytesseract.image_to_string(pil_image, config=OCR_CONFIG)

    results = parse_ocr_text(text)
    return results


def parse_ocr_text(text: str) -> list[dict]:
    """
    Parse OCR text to extract race positions.

    The expected format is lines like:
    "1st Maruzensky Kysix"
    "2nd Haru Urara Sebaxd321"
    etc.

    Args:
        text: Raw OCR text

    Returns:
        List of dictionaries with placement, character_name, and user_name
    """
    results = []
    lines = text.strip().split("\n")

    # Pattern to match placement numbers (1st, 2nd, 3rd, etc. or just numbers)
    placement_pattern = re.compile(r"^(\d+)(?:st|nd|rd|th)?[\.\s:]?\s*(.+)", re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = placement_pattern.match(line)
        if match:
            placement = int(match.group(1))
            rest = match.group(2).strip()

            # Try to split the rest into character name and user name
            # This is heuristic - typically character name comes first, then user name
            parts = rest.split()
            if len(parts) >= 2:
                # Assume last part is user name, rest is character name
                user_name = parts[-1]
                character_name = " ".join(parts[:-1])
            elif len(parts) == 1:
                character_name = parts[0]
                user_name = "Unknown"
            else:
                continue

            results.append(
                {
                    "placement": placement,
                    "character_name": character_name,
                    "user_name": user_name,
                }
            )

    # Sort by placement
    results.sort(key=lambda x: x["placement"])
    return results


def format_placement(placement: int) -> str:
    """
    Format a placement number with ordinal suffix.

    Args:
        placement: The placement number

    Returns:
        Formatted string like "1st", "2nd", "3rd", etc.
    """
    if 11 <= placement <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(placement % 10, "th")
    return f"{placement}{suffix}"


def write_results(
    results: dict[str, list[dict]], output_path: Path
) -> None:
    """
    Write extracted race results to a text file.

    Args:
        results: Dictionary mapping image names to lists of race positions
        output_path: Path to the output file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("RACE RESULTS - Uma Musume Tournament\n")
        f.write("=" * 60 + "\n\n")

        for image_name, positions in results.items():
            f.write(f"Race: {image_name}\n")
            f.write("-" * 40 + "\n")

            if positions:
                for pos in positions:
                    placement_str = format_placement(pos["placement"])
                    f.write(
                        f"{placement_str}: {pos['character_name']} - {pos['user_name']}\n"
                    )
            else:
                f.write("No positions extracted (OCR could not parse this image)\n")

            f.write("\n")

        f.write("=" * 60 + "\n")
        f.write("End of Results\n")
        f.write("=" * 60 + "\n")


def main() -> None:
    """Main entry point for the screenshot processing script."""
    project_root = get_project_root()
    screenshots_dir = project_root / "screenshots"
    cropped_dir = screenshots_dir / "cropped"
    output_file = screenshots_dir / "race_results.txt"

    # Ensure directories exist
    screenshots_dir.mkdir(exist_ok=True)
    cropped_dir.mkdir(exist_ok=True)

    print("UmaTurniej Screenshot Processor")
    print("=" * 40)

    # Load screenshots
    screenshots = load_screenshots(screenshots_dir)

    if not screenshots:
        print(f"No PNG files found in {screenshots_dir}")
        print("Please add race screenshots to the screenshots directory.")
        return

    print(f"Found {len(screenshots)} screenshot(s) to process")

    all_results = {}

    for screenshot in screenshots:
        print(f"\nProcessing: {screenshot.name}")

        try:
            # Crop the left half
            cropped_path = crop_left_half(screenshot, cropped_dir)
            print(f"  - Cropped image saved to: {cropped_path.name}")

            # Extract race positions using OCR
            positions = extract_race_positions(cropped_path)
            print(f"  - Extracted {len(positions)} position(s)")

            all_results[screenshot.name] = positions

        except (ValueError, FileNotFoundError) as e:
            print(f"  - Error processing {screenshot.name}: {e}")
            all_results[screenshot.name] = []
        except pytesseract.TesseractError as e:
            print(f"  - OCR error processing {screenshot.name}: {e}")
            all_results[screenshot.name] = []
        except cv2.error as e:
            print(f"  - Image processing error for {screenshot.name}: {e}")
            all_results[screenshot.name] = []
        except Exception as e:  # noqa: BLE001
            print(f"  - Unexpected error processing {screenshot.name}: {e}")
            print(f"    Traceback: {traceback.format_exc()}")
            all_results[screenshot.name] = []

    # Write results to file
    write_results(all_results, output_file)
    print(f"\nResults written to: {output_file}")

    # Print summary to console
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    for image_name, positions in all_results.items():
        print(f"\n{image_name}:")
        for pos in positions:
            placement_str = format_placement(pos["placement"])
            print(f"  {placement_str}: {pos['character_name']} - {pos['user_name']}")


if __name__ == "__main__":
    main()
