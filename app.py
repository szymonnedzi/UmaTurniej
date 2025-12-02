#!/usr/bin/env python3
"""
UmaTurniej Flask API
Provides REST API endpoints for uploading screenshots and extracting race data.
"""

import os
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from ocr_extraction.extract_ocr_data import (
    extract_text_from_image,
    format_results,
    parse_entry_number,
)
from screenshot_processing.process_screenshots import extract_entry_snippets

app = Flask(__name__)

# Configuration
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = Path(__file__).parent / "screenshots" / "uploads"
CROPPED_FOLDER = Path(__file__).parent / "screenshots" / "cropped"

# Ensure directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
CROPPED_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index() -> dict[str, Any]:
    """API root endpoint with information about available endpoints."""
    return jsonify({
        "name": "UmaTurniej API",
        "version": "1.0.0",
        "description": "Screenshot processing and OCR extraction API for Uma Musume Tournament",
        "endpoints": {
            "/": "This help message",
            "/api/upload": "POST - Upload a screenshot and extract race data",
            "/api/health": "GET - Health check endpoint"
        }
    })


@app.route("/api/health", methods=["GET"])
def health() -> dict[str, Any]:
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "UmaTurniej API"
    })


@app.route("/api/upload", methods=["POST"])
def upload_screenshot() -> tuple[dict[str, Any], int]:
    """
    Upload a screenshot and extract race data.
    
    Expected: multipart/form-data with 'file' field containing the image.
    
    Returns:
        JSON response with extraction results and HTTP status code.
    """
    # Check if file is present in request
    if "file" not in request.files:
        return jsonify({
            "error": "No file provided",
            "message": "Please provide a file in the 'file' field"
        }), 400
    
    file = request.files["file"]
    
    # Check if file was selected
    if file.filename == "":
        return jsonify({
            "error": "No file selected",
            "message": "Please select a file to upload"
        }), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type",
            "message": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        upload_path = UPLOAD_FOLDER / filename
        file.save(str(upload_path))
        
        # Step 1: Extract entry snippets from the screenshot
        snippet_paths = extract_entry_snippets(upload_path, CROPPED_FOLDER)
        
        if not snippet_paths:
            return jsonify({
                "error": "No entries extracted",
                "message": "Could not extract race entries from the screenshot"
            }), 500
        
        # Step 2: Perform OCR on each snippet
        results = []
        for snippet_path in snippet_paths:
            entry_num = parse_entry_number(snippet_path.name)
            if entry_num is None:
                continue
            
            # Extract text data from the snippet
            text_data = extract_text_from_image(snippet_path)
            
            result = {
                "position": text_data.get("position") or f"Entry {entry_num}",
                "character": text_data["character"] or "[Unknown Character]",
                "player": text_data["player"] or "[Unknown Player]",
                "source_snippet": snippet_path.name
            }
            results.append(result)
        
        # Clean up uploaded file (optional - comment out if you want to keep uploads)
        # upload_path.unlink()
        
        return jsonify({
            "status": "success",
            "message": f"Processed screenshot: {filename}",
            "screenshot": filename,
            "entries_extracted": len(snippet_paths),
            "results": results
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Processing failed",
            "message": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error: Any) -> tuple[dict[str, Any], int]:
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error: Any) -> tuple[dict[str, Any], int]:
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == "__main__":
    # Run the Flask development server
    # For production, use a WSGI server like gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
