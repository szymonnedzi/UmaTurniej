"""
UmaTurniej - Screenshot Processing and OCR Application
Main entry point for the application.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from extract_ocr_data import main as extract_ocr_main
from process_screenshots import main as process_screenshots_main


def process_and_extract() -> Path | None:
    """
    Process screenshots and extract OCR data.
    
    Returns:
        Path to the generated race_results.txt file if successful, None otherwise
    """
    print("=" * 50)
    print("UmaTurniej - Screenshot Processing and OCR")
    print("=" * 50)
    print()
    
    # Step 1: Process screenshots into cropped snippets
    print("Step 1: Processing screenshots...")
    print("-" * 50)
    snippets_dir = process_screenshots_main()
    print()
    
    if snippets_dir is None:
        print("✗ Screenshot processing failed. Aborting.")
        return None
    
    # Step 2: Extract OCR data from cropped snippets
    print("Step 2: Extracting OCR data...")
    print("-" * 50)
    output_file = extract_ocr_main()
    print()
    
    if output_file is None:
        print("✗ OCR extraction failed. Aborting.")
        return None
    
    # Report success
    print("=" * 50)
    print(f"✓ Processing complete!")
    print(f"✓ Results saved to: {output_file}")
    print("=" * 50)
    
    return output_file


def main() -> None:
    """Main entry point for the application."""
    process_and_extract()


if __name__ == "__main__":
    main()
