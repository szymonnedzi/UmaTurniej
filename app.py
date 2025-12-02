#!/usr/bin/env python3
"""
UmaTurniej Flask API
Provides REST API endpoints for uploading screenshots and extracting race data.
"""

from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from flasgger import Swagger

from ocr_extraction.extract_ocr_data import (
    extract_text_from_image,
    parse_entry_number,
)
from screenshot_processing.process_screenshots import extract_entry_snippets

app = Flask(__name__)

# Configure Swagger/OpenAPI 3.0 specification
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
    "openapi": "3.0.0"
}

swagger_template = {
    "openapi": "3.0.0",
    "info": {
        "title": "UmaTurniej API",
        "description": "Screenshot processing and OCR extraction API for Uma Musume Tournament",
        "version": "1.0.0",
        "contact": {
            "name": "UmaTurniej",
            "url": "https://github.com/szymonnedzi/UmaTurniej"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Local development server"
        }
    ],
    "tags": [
        {
            "name": "general",
            "description": "General API information and health endpoints"
        },
        {
            "name": "screenshot",
            "description": "Screenshot processing and OCR extraction"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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
    """API root endpoint with information about available endpoints.
    ---
    tags:
      - general
    summary: API Information
    description: Returns basic information about the API and available endpoints
    responses:
      200:
        description: API information
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: UmaTurniej API
                version:
                  type: string
                  example: 1.0.0
                description:
                  type: string
                  example: Screenshot processing and OCR extraction API for Uma Musume Tournament
                endpoints:
                  type: object
                  properties:
                    /:
                      type: string
                      example: This help message
                    /api/upload:
                      type: string
                      example: POST - Upload a screenshot and extract race data
                    /api/health:
                      type: string
                      example: GET - Health check endpoint
                    /api/docs:
                      type: string
                      example: GET - OpenAPI/Swagger UI documentation
    """
    return jsonify({
        "name": "UmaTurniej API",
        "version": "1.0.0",
        "description": "Screenshot processing and OCR extraction API for Uma Musume Tournament",
        "endpoints": {
            "/": "This help message",
            "/api/upload": "POST - Upload a screenshot and extract race data",
            "/api/health": "GET - Health check endpoint",
            "/api/docs": "GET - OpenAPI/Swagger UI documentation"
        }
    })


@app.route("/api/health", methods=["GET"])
def health() -> dict[str, Any]:
    """Health check endpoint.
    ---
    tags:
      - general
    summary: Health Check
    description: Returns the health status of the API service
    responses:
      200:
        description: Service is healthy
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
                service:
                  type: string
                  example: UmaTurniej API
    """
    return jsonify({
        "status": "healthy",
        "service": "UmaTurniej API"
    })


@app.route("/api/upload", methods=["POST"])
def upload_screenshot() -> tuple[dict[str, Any], int]:
    """Upload a screenshot and extract race data.
    ---
    tags:
      - screenshot
    summary: Upload Screenshot
    description: |
      Upload a race screenshot and extract race data using OCR.
      The endpoint processes the screenshot, extracts individual entry snippets,
      and performs OCR to extract position, character name, and player name.
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - file
            properties:
              file:
                type: string
                format: binary
                description: Race screenshot image file (PNG, JPG, or JPEG)
    responses:
      200:
        description: Screenshot processed successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                message:
                  type: string
                  example: Processed screenshot filename.jpg
                screenshot:
                  type: string
                  example: filename.jpg
                entries_extracted:
                  type: integer
                  example: 7
                results:
                  type: array
                  items:
                    type: object
                    properties:
                      position:
                        type: string
                        example: 1st
                      character:
                        type: string
                        example: Special Week
                      player:
                        type: string
                        example: Player123
                      source_snippet:
                        type: string
                        example: filename_entry_1.png
      400:
        description: Bad request - invalid file or missing file
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: No file provided
                message:
                  type: string
                  example: Please provide a file in the 'file' field
            examples:
              no_file:
                value:
                  error: No file provided
                  message: Please provide a file in the 'file' field
              no_selection:
                value:
                  error: No file selected
                  message: Please select a file to upload
              invalid_type:
                value:
                  error: Invalid file type
                  message: "Allowed file types: png, jpg, jpeg"
      500:
        description: Internal server error during processing
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Processing failed
                message:
                  type: string
                  example: Error details
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
    app.run(host="0.0.0.0", port=5000, debug=False)
