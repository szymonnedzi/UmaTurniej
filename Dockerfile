# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - tesseract-ocr: Required for OCR functionality
# - tesseract-ocr-eng: English language data for Tesseract
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# Note: --trusted-host flags may be needed in restricted network environments
# In production, these can be removed if your network allows SSL verification
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application files
COPY . .

# Create screenshots directory structure
RUN mkdir -p /app/screenshots/cropped

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command - run the main application
CMD ["python", "main.py"]
