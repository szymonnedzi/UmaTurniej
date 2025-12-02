"""
UmaTurniej - Screenshot Processing and OCR Application
Main entry point for the application.
"""

import sys


def main() -> None:
    """Main entry point for the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run Flask API server
        from app import app
        print("Starting UmaTurniej Flask API server...")
        print("Server will be available at http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        # Default behavior
        print("UmaTurniej - Screenshot Processing and OCR Application")
        print("\nAvailable commands:")
        print("  python main.py api              - Start Flask API server")
        print("  python screenshot_processing/process_screenshots.py - Extract snippets")
        print("  python ocr_extraction/extract_ocr_data.py           - Extract OCR data")


if __name__ == "__main__":
    main()
