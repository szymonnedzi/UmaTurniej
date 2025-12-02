"""
UmaTurniej - Screenshot Processing and OCR Application
Main entry point for the application.
"""

import importlib.util
import sys
from pathlib import Path


def _load_module_from_path(module_name: str, file_path: Path):
    """Dynamically load a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    
    project_root = Path(__file__).parent
    
    # Load the script modules dynamically from their new locations
    process_screenshots = _load_module_from_path(
        "process_screenshots",
        project_root / "screenshot_processing" / "process_screenshots.py"
    )
    extract_ocr_data = _load_module_from_path(
        "extract_ocr_data",
        project_root / "ocr_extraction" / "extract_ocr_data.py"
    )
    
    # Step 1: Process screenshots into cropped snippets
    print("Step 1: Processing screenshots...")
    print("-" * 50)
    snippets_dir = process_screenshots.main()
    print()
    
    if snippets_dir is None:
        print("✗ Screenshot processing failed. Aborting.")
        return None
    
    # Step 2: Extract OCR data from cropped snippets
    print("Step 2: Extracting OCR data...")
    print("-" * 50)
    output_file = extract_ocr_data.main()
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


def main() -> int:
    """Main entry point for the application.
    
    Returns:
        0 if successful, 1 if failed
    """
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run Flask API server
        from app import app
        print("Starting UmaTurniej Flask API server...")
        print("Server will be available at http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
        return 0
    elif len(sys.argv) > 1 and sys.argv[1] == "help":
        # Show help
        print("UmaTurniej - Screenshot Processing and OCR Application")
        print("\nAvailable commands:")
        print("  python main.py                  - Run unified workflow (process + extract)")
        print("  python main.py api              - Start Flask API server")
        print("  python main.py help             - Show this help message")
        print("\nManual processing:")
        print("  python screenshot_processing/process_screenshots.py - Extract snippets")
        print("  python ocr_extraction/extract_ocr_data.py           - Extract OCR data")
        return 0
    else:
        # Default: Run unified workflow
        result = process_and_extract()
        return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
