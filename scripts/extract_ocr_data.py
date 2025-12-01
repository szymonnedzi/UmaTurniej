#!/usr/bin/env python3
"""
OCR Data Extraction Script for UmaTurniej
Extracts position, character name, and player name from cropped screenshot snippets.

This script:
1. Loads cropped entry images from /screenshots/cropped/
2. Uses OCR to extract character and player names
3. Attempts to detect position (1st, 2nd, 8th, etc.) from the image via OCR
4. Falls back to entry number from filename if OCR position detection fails
5. Outputs results to a text file
"""

import re
from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageOps

# Known Uma Musume character names for better matching
KNOWN_CHARACTERS = [
    "Maruzensky", "Haru Urara", "El Condor Pasa", "Smart Falcon",
    "Taiki Shuttle", "Silence Suzuka", "Tokai Teio", "Mejiro McQueen",
    "Special Week", "Grass Wonder", "Vodka", "Daiwa Scarlet",
    "Gold Ship", "Oguri Cap", "Rice Shower", "Symboli Rudolf",
    "Air Groove", "Agnes Tachyon", "Admire Vega", "Seiun Sky",
    "King Halo", "Super Creek", "Narita Brian", "Nice Nature",
    "Mihono Bourbon", "Mayano Top Gun", "Manhattan Cafe", "Zenno Rob Roy",
    "Twin Turbo", "Sakura Bakushin O", "Nakayama Festa", "Ines Fujin",
    "Agnes Digital", "Seeking the Pearl", "Winning Ticket", "Hishi Amazon",
    "Tamamo Cross", "Fine Motion", "Biwa Hayahide", "Air Shakur",
    "Meisho Doto", "Eishin Flash", "Curren Chan", "T.M. Opera O",
    "Narita Taishin", "Sweep Tosho", "Hishi Akebono", "Yaeno Muteki",
    "Sakura Chiyono O", "Mejiro Ryan", "Mejiro Dober", "Mejiro Palmer",
    "Mejiro Ardan", "Bamboo Memory", "Matikanefukukitaru", "Nishino Flower",
    "Yukino Bijin", "Daitaku Helios", "Copano Rickey", "Kitasan Black",
    "Satono Diamond", "Wonder Acute", "Katsuragi Ace", "Inari One",
    "Sirius Symboli", "Marvelous Sunday", "Shinko Windy", "Sakura Laurel",
    "Neo Universe", "Transcend", "Satono Crown", "Duramente",
    "Machikane Tannhauser", "Hokko Tarumae", "K.S. Miracle",
]

# Position ordinal suffixes
ORDINAL_SUFFIX = {1: "st", 2: "nd", 3: "rd"}


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_ordinal(n: int) -> str:
    """Convert a number to its ordinal representation (1st, 2nd, 3rd, etc.)."""
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = ORDINAL_SUFFIX.get(n % 10, "th")
    return f"{n}{suffix}"


def extract_position_from_image(img: Image.Image) -> str | None:
    """
    Attempt to extract the position (1st, 2nd, 3rd, etc.) from the left side of the image.

    The position is displayed as a stylized ordinal number on the left side of each
    race entry snippet.

    Args:
        img: PIL Image object of the cropped entry

    Returns:
        Position string (e.g., "8th") if detected, None otherwise
    """
    # Crop left portion where position is shown (approximately first 150 pixels)
    left_region = img.crop((0, 0, 150, img.height))

    # Try multiple preprocessing approaches to improve OCR accuracy
    gray = ImageOps.grayscale(left_region)
    preprocessing_attempts = [
        gray,
        ImageOps.invert(gray),
        ImageEnhance.Contrast(gray).enhance(2.0),
    ]

    # Try different Tesseract Page Segmentation Modes (PSM) for position detection
    # PSM 7: Treat image as a single text line
    # PSM 8: Treat image as a single word
    # PSM 6: Assume a single uniform block of text
    # PSM 11: Sparse text - find as much text as possible
    psm_modes = [7, 8, 6, 11]

    for attempt_img in preprocessing_attempts:
        for psm in psm_modes:
            try:
                data = pytesseract.image_to_data(
                    attempt_img,
                    output_type=pytesseract.Output.DICT,
                    config=f"--psm {psm}",
                )

                for word in data["text"]:
                    word = word.strip().lower()
                    if not word:
                        continue
                    # Check for ordinal patterns (1st, 2nd, 3rd, 4th, etc.)
                    match = re.match(r"^(\d+)(st|nd|rd|th)$", word)
                    if match:
                        num = int(match.group(1))
                        return get_ordinal(num)
            except (ValueError, RuntimeError):
                pass

    return None


def extract_text_from_image(image_path: Path) -> dict:
    """
    Extract character and player name from a cropped entry image using OCR.

    Uses position-based filtering to separate character name from player name,
    since they appear at different Y coordinates in the image.

    Args:
        image_path: Path to the cropped entry image

    Returns:
        Dictionary with 'character', 'player', and 'position' keys
    """
    img = Image.open(image_path)

    # Try to extract position from the left side of the image
    detected_position = extract_position_from_image(img)

    # Get OCR data with bounding boxes
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Title/achievement texts to filter out (these appear in the top-right badge)
    TITLE_WORDS = {
        "finals", "champion", "witness", "legend", "record", "holder",
        "dream", "team", "ideal", "idol", "to",
    }

    # Collect all valid words with their positions
    all_words = []

    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue

        confidence = data["conf"][i]
        x = data["left"][i]
        y = data["top"][i]

        # Filter by position - names are on the right side of the image
        if x >= 200 and confidence > 40:
            # Skip common noise patterns
            if word in ["@", "(i)", "|", "_", "-", "(", ")", "[", "]", "|,", "B", "="]:
                continue
            # Skip single characters that are likely noise
            if len(word) == 1:
                continue
            # Skip numbers that might be rankings
            if word.isdigit() and len(word) <= 2:
                continue
            # Clean words ending with (i)
            clean_word = re.sub(r"\(i\)$", "", word).strip()
            if not clean_word:
                continue
            word = clean_word

            # Skip title/achievement words (case-insensitive)
            if word.lower() in TITLE_WORDS:
                continue

            all_words.append((y, word))

    # Sort all words by Y position
    all_words.sort(key=lambda x: x[0])

    # Categorize words into character name and player name
    # Based on observed patterns:
    # - If we have 2+ lines, first line(s) = character, last line = player
    # - If we have only 1 line, it's likely a player name
    character_words = []
    player_words = []

    if len(all_words) == 0:
        pass  # No words found
    elif len(all_words) == 1:
        # Single word - assume it's player name
        player_words = all_words
    else:
        # Multiple words - group by Y proximity
        # Words within 15px of each other are on the same line
        lines = []
        current_line = [all_words[0]]
        for y, word in all_words[1:]:
            if abs(y - current_line[-1][0]) <= 15:
                current_line.append((y, word))
            else:
                lines.append(current_line)
                current_line = [(y, word)]
        lines.append(current_line)

        if len(lines) == 1:
            # All words on same line - likely player name only
            player_words = lines[0]
        else:
            # Multiple lines - character name on upper line(s), player on lower
            for line in lines[:-1]:
                character_words.extend(line)
            player_words = lines[-1]

    character_name = " ".join(w[1] for w in character_words)
    player_name = " ".join(w[1] for w in player_words)

    # Clean up names - remove common OCR artifacts
    character_name = re.sub(r"\s*\([^)]*\)\s*$", "", character_name)
    player_name = re.sub(r"\s*\([^)]*\)\s*$", "", player_name)
    player_name = re.sub(r"\s*@\s*$", "", player_name)

    return {
        "character": character_name.strip(),
        "player": player_name.strip(),
        "position": detected_position,
    }


def parse_entry_number(filename: str) -> int | None:
    """
    Extract the entry number from a filename.

    Expected format: {screenshot_name}_entry_{n}.png

    Args:
        filename: Name of the cropped image file

    Returns:
        Entry number (1-7), or None if not found
    """
    match = re.search(r"_entry_(\d+)\.png$", filename)
    if match:
        return int(match.group(1))
    return None


def process_cropped_images(cropped_dir: Path) -> list[dict]:
    """
    Process all cropped entry images and extract OCR data.

    Args:
        cropped_dir: Path to the directory containing cropped images

    Returns:
        List of dictionaries with position, character, player, and source file
    """
    results = []

    # Get all PNG files in the cropped directory
    image_files = sorted(cropped_dir.glob("*.png"))

    for image_path in image_files:
        if image_path.name == ".gitkeep":
            continue

        entry_num = parse_entry_number(image_path.name)
        if entry_num is None:
            print(f"  Warning: Could not parse entry number from {image_path.name}")
            continue

        # Extract text data (including OCR-detected position)
        text_data = extract_text_from_image(image_path)

        # Use OCR-detected position if available, otherwise fall back to entry number
        position = text_data.get("position")
        if position is None:
            position = get_ordinal(entry_num)
            position_source = "filename"
        else:
            position_source = "OCR"

        result = {
            "position": position,
            "position_source": position_source,
            "character": text_data["character"],
            "player": text_data["player"],
            "source_file": image_path.name,
        }

        results.append(result)

    return results


def format_results(results: list[dict]) -> str:
    """
    Format extraction results as a text report.

    Args:
        results: List of extraction results

    Returns:
        Formatted text string
    """
    lines = []
    lines.append("UmaTurniej Race Results - OCR Extraction")
    lines.append("=" * 50)
    lines.append("")

    # Group results by source screenshot
    current_screenshot = None

    for result in results:
        # Extract base screenshot name (without _entry_N)
        base_name = re.sub(r"_entry_\d+\.png$", "", result["source_file"])

        if base_name != current_screenshot:
            if current_screenshot is not None:
                lines.append("")  # Add blank line between screenshots
            lines.append(f"Screenshot: {base_name}")
            lines.append("-" * 40)
            current_screenshot = base_name

        position = result["position"]
        character = result["character"] or "[Unknown Character]"
        player = result["player"] or "[Unknown Player]"

        lines.append(f"  {position}: {character} - {player}")

    lines.append("")
    lines.append("=" * 50)
    lines.append(f"Total entries processed: {len(results)}")

    return "\n".join(lines)


def main() -> None:
    """Main entry point for the OCR extraction script."""
    project_root = get_project_root()
    cropped_dir = project_root / "screenshots" / "cropped"
    output_file = project_root / "race_results.txt"

    print("UmaTurniej OCR Data Extraction")
    print("=" * 45)

    if not cropped_dir.exists():
        print(f"Error: Cropped directory not found: {cropped_dir}")
        return

    # Find all cropped images (excluding .gitkeep and other non-image files)
    image_files = [
        f for f in cropped_dir.glob("*.png")
        if f.name != ".gitkeep" and not f.name.startswith(".")
    ]
    image_count = len(image_files)
    if image_count == 0:
        print(f"No cropped images found in {cropped_dir}")
        print("Run scripts/process_screenshots.py first to generate cropped images.")
        return

    print(f"Found {image_count} cropped image(s) to process")
    print()

    # Process images
    results = process_cropped_images(cropped_dir)

    # Format and save results
    output_text = format_results(results)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(output_text)
    print()
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
