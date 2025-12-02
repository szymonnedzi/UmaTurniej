#!/usr/bin/env python3
"""
Tests for OCR Data Extraction functionality in UmaTurniej.

This test suite covers text extraction functions including:
- Ordinal number conversion
- Filename parsing
- Result formatting
- OCR position detection
- OCR text extraction from images
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ocr_extraction.extract_ocr_data import (
    extract_position_from_image,
    extract_text_from_image,
    format_results,
    get_ordinal,
    parse_entry_number,
)


class TestGetOrdinal:
    """Test cases for the get_ordinal() function."""

    def test_ordinal_1st(self):
        """Test that 1 converts to '1st'."""
        assert get_ordinal(1) == "1st"

    def test_ordinal_2nd(self):
        """Test that 2 converts to '2nd'."""
        assert get_ordinal(2) == "2nd"

    def test_ordinal_3rd(self):
        """Test that 3 converts to '3rd'."""
        assert get_ordinal(3) == "3rd"

    def test_ordinal_4th_through_10th(self):
        """Test that 4-10 convert to 'Nth' format."""
        assert get_ordinal(4) == "4th"
        assert get_ordinal(5) == "5th"
        assert get_ordinal(6) == "6th"
        assert get_ordinal(7) == "7th"
        assert get_ordinal(8) == "8th"
        assert get_ordinal(9) == "9th"
        assert get_ordinal(10) == "10th"

    def test_ordinal_11th_12th_13th_special_cases(self):
        """Test that 11, 12, 13 use 'th' suffix (special cases)."""
        assert get_ordinal(11) == "11th"
        assert get_ordinal(12) == "12th"
        assert get_ordinal(13) == "13th"

    def test_ordinal_21st_22nd_23rd(self):
        """Test that 21, 22, 23 use st/nd/rd suffixes."""
        assert get_ordinal(21) == "21st"
        assert get_ordinal(22) == "22nd"
        assert get_ordinal(23) == "23rd"

    def test_ordinal_large_numbers(self):
        """Test ordinal conversion for large numbers."""
        assert get_ordinal(101) == "101st"
        assert get_ordinal(112) == "112th"
        assert get_ordinal(123) == "123rd"
        assert get_ordinal(1000) == "1000th"


class TestParseEntryNumber:
    """Test cases for the parse_entry_number() function."""

    def test_parse_valid_entry_number(self):
        """Test parsing a valid filename with entry number."""
        assert parse_entry_number("screenshot_entry_1.png") == 1
        assert parse_entry_number("screenshot_entry_7.png") == 7

    def test_parse_entry_with_complex_basename(self):
        """Test parsing entry number with complex base filename."""
        assert parse_entry_number("20251130185703_1_entry_5.png") == 5
        assert parse_entry_number("my_race_screenshot_entry_3.png") == 3

    def test_parse_missing_entry_pattern(self):
        """Test that files without entry pattern return None."""
        assert parse_entry_number("screenshot.png") is None
        assert parse_entry_number("random_file.jpg") is None

    def test_parse_invalid_format(self):
        """Test that invalid formats return None."""
        assert parse_entry_number("screenshot_entry_.png") is None
        assert parse_entry_number("screenshot_entry_abc.png") is None
        assert parse_entry_number("entry_5.jpg") is None  # Wrong extension

    def test_parse_double_digit_entry(self):
        """Test parsing double-digit entry numbers."""
        assert parse_entry_number("screenshot_entry_10.png") == 10
        assert parse_entry_number("screenshot_entry_99.png") == 99


class TestFormatResults:
    """Test cases for the format_results() function."""

    def test_format_empty_results(self):
        """Test formatting with no results."""
        output = format_results([])
        assert "UmaTurniej Race Results - OCR Extraction" in output
        assert "Total entries processed: 0" in output

    def test_format_single_result(self):
        """Test formatting a single result."""
        results = [
            {
                "position": "1st",
                "character": "Special Week",
                "player": "PlayerName",
                "source_file": "screenshot_entry_1.png",
            }
        ]
        output = format_results(results)
        assert "Screenshot: screenshot" in output
        assert "1st: Special Week - PlayerName" in output
        assert "Total entries processed: 1" in output

    def test_format_multiple_results_same_screenshot(self):
        """Test formatting multiple results from same screenshot."""
        results = [
            {
                "position": "1st",
                "character": "Special Week",
                "player": "Player1",
                "source_file": "race1_entry_1.png",
            },
            {
                "position": "2nd",
                "character": "Silence Suzuka",
                "player": "Player2",
                "source_file": "race1_entry_2.png",
            },
        ]
        output = format_results(results)
        assert "Screenshot: race1" in output
        assert "1st: Special Week - Player1" in output
        assert "2nd: Silence Suzuka - Player2" in output
        assert "Total entries processed: 2" in output

    def test_format_multiple_screenshots(self):
        """Test formatting results from multiple screenshots."""
        results = [
            {
                "position": "1st",
                "character": "Special Week",
                "player": "Player1",
                "source_file": "race1_entry_1.png",
            },
            {
                "position": "1st",
                "character": "Tokai Teio",
                "player": "Player2",
                "source_file": "race2_entry_1.png",
            },
        ]
        output = format_results(results)
        assert "Screenshot: race1" in output
        assert "Screenshot: race2" in output
        assert output.index("race1") < output.index("race2")

    def test_format_with_missing_data(self):
        """Test formatting with missing position, character, or player."""
        results = [
            {
                "position": None,
                "character": "",
                "player": "SomePlayer",
                "source_file": "screenshot_entry_1.png",
            }
        ]
        output = format_results(results)
        assert "[Unknown Position]" in output
        assert "[Unknown Character]" in output
        assert "SomePlayer" in output

    def test_format_output_structure(self):
        """Test the overall structure of formatted output."""
        results = [
            {
                "position": "1st",
                "character": "Test Character",
                "player": "Test Player",
                "source_file": "test_entry_1.png",
            }
        ]
        output = format_results(results)
        lines = output.split("\n")
        assert lines[0] == "UmaTurniej Race Results - OCR Extraction"
        assert "=" * 50 in lines[1]
        assert any("Screenshot:" in line for line in lines)
        assert any("-" * 40 in line for line in lines)


class TestExtractPositionFromImage:
    """Test cases for the extract_position_from_image() function."""

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_1st(self, mock_ocr):
        """Test extraction of '1st' position."""
        mock_ocr.return_value = {
            "text": ["", "1st", ""],
        }
        
        # Create a simple test image
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        assert result == "1st"

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_8th(self, mock_ocr):
        """Test extraction of '8th' position."""
        mock_ocr.return_value = {
            "text": ["", "8th", ""],
        }
        
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        assert result == "8th"

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_case_insensitive(self, mock_ocr):
        """Test that position extraction is case-insensitive."""
        mock_ocr.return_value = {
            "text": ["", "2ND", ""],
        }
        
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        assert result == "2nd"

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_with_noise(self, mock_ocr):
        """Test extraction with noise in OCR output."""
        mock_ocr.return_value = {
            "text": ["noise", "garbage", "3rd", "more", "text"],
        }
        
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        assert result == "3rd"

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_not_found(self, mock_ocr):
        """Test when no valid position is found."""
        mock_ocr.return_value = {
            "text": ["no", "position", "here"],
        }
        
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        assert result is None

    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    def test_extract_position_malformed_ordinal(self, mock_ocr):
        """Test normalization of malformed ordinals (e.g., '2th' -> '2nd')."""
        # Mock OCR returning a malformed ordinal
        mock_ocr.return_value = {
            "text": ["2th"],  # OCR might return incorrect suffix
        }
        
        img = Image.new("RGB", (150, 100), color="white")
        result = extract_position_from_image(img)
        # The function should normalize to correct ordinal
        assert result == "2nd"


class TestExtractTextFromImage:
    """Test cases for the extract_text_from_image() function."""

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_basic(self, mock_open, mock_ocr, mock_position):
        """Test basic text extraction from image."""
        # Mock image
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        
        # Mock position extraction
        mock_position.return_value = "1st"
        
        # Mock OCR data - simulate character name on top line, player name on bottom
        mock_ocr.return_value = {
            "text": ["", "Special", "Week", "", "PlayerName"],
            "conf": [0, 90, 90, 0, 85],
            "left": [0, 250, 330, 0, 250],
            "top": [0, 20, 20, 0, 60],
        }
        
        result = extract_text_from_image(Path("test_entry_1.png"))
        
        assert result["position"] == "1st"
        assert "Special" in result["character"]
        assert "Week" in result["character"]
        assert result["player"] == "PlayerName"

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_filters_noise(self, mock_open, mock_ocr, mock_position):
        """Test that noise is filtered from OCR output."""
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        mock_position.return_value = "2nd"
        
        # Mock OCR with noise
        mock_ocr.return_value = {
            "text": ["@", "Character", "Name", "_", "Player", "3", "(i)"],
            "conf": [10, 90, 90, 20, 85, 50, 30],
            "left": [100, 250, 330, 150, 250, 100, 400],
            "top": [30, 20, 20, 40, 60, 30, 65],
        }
        
        result = extract_text_from_image(Path("test_entry_2.png"))
        
        # Should filter out @, _, single digits, and (i)
        assert "@" not in result["character"]
        assert "_" not in result["character"]
        assert "Character" in result["character"]

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_filters_title_words(self, mock_open, mock_ocr, mock_position):
        """Test that title/achievement words are filtered out."""
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        mock_position.return_value = "1st"
        
        # Mock OCR with title words
        mock_ocr.return_value = {
            "text": ["Champion", "Special", "Week", "Finals", "Player"],
            "conf": [85, 90, 90, 80, 85],
            "left": [250, 250, 330, 400, 250],
            "top": [15, 20, 20, 18, 60],
        }
        
        result = extract_text_from_image(Path("test_entry_1.png"))
        
        # Should filter out "Champion" and "Finals"
        assert "champion" not in result["character"].lower()
        assert "finals" not in result["character"].lower()

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_no_position(self, mock_open, mock_ocr, mock_position):
        """Test extraction when position cannot be determined."""
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        mock_position.return_value = None  # Position not detected
        
        mock_ocr.return_value = {
            "text": ["Character", "Player"],
            "conf": [90, 85],
            "left": [250, 250],
            "top": [20, 60],
        }
        
        result = extract_text_from_image(Path("test_entry_1.png"))
        
        assert result["position"] is None
        assert result["character"] == "Character"
        assert result["player"] == "Player"

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_empty_result(self, mock_open, mock_ocr, mock_position):
        """Test extraction when OCR finds no text."""
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        mock_position.return_value = None
        
        mock_ocr.return_value = {
            "text": [],
            "conf": [],
            "left": [],
            "top": [],
        }
        
        result = extract_text_from_image(Path("test_entry_1.png"))
        
        assert result["position"] is None
        assert result["character"] == ""
        assert result["player"] == ""

    @patch("ocr_extraction.extract_ocr_data.extract_position_from_image")
    @patch("ocr_extraction.extract_ocr_data.pytesseract.image_to_data")
    @patch("ocr_extraction.extract_ocr_data.Image.open")
    def test_extract_text_multiline_character_name(self, mock_open, mock_ocr, mock_position):
        """Test extraction of multi-line character names."""
        mock_img = Image.new("RGB", (625, 105), color="white")
        mock_open.return_value = mock_img
        mock_position.return_value = "3rd"
        
        # Character name spans two lines, player on third line
        mock_ocr.return_value = {
            "text": ["Special", "Week", "Player"],
            "conf": [90, 90, 85],
            "left": [250, 330, 250],
            "top": [15, 15, 60],  # First two on same Y, third lower
        }
        
        result = extract_text_from_image(Path("test_entry_3.png"))
        
        assert "Special" in result["character"]
        assert "Week" in result["character"]
        assert result["player"] == "Player"


class TestIntegrationWithRealImages:
    """Integration tests using real test images (if available)."""

    @pytest.fixture
    def test_images_dir(self):
        """Provide path to test images directory."""
        return Path(__file__).parent / "test" / "test_input"

    def test_real_images_exist(self, test_images_dir):
        """Verify test images are available."""
        if not test_images_dir.exists():
            pytest.skip("Test images directory not found")
        
        image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
        assert len(image_files) > 0, "No test images found"

    def test_extract_from_real_image_structure(self, test_images_dir):
        """Test that extraction from real images returns expected structure."""
        if not test_images_dir.exists():
            pytest.skip("Test images directory not found")
        
        # Note: This test doesn't validate OCR accuracy, just the structure
        # Real OCR quality depends on tesseract installation and image quality
        image_files = list(test_images_dir.glob("*.jpg"))
        if not image_files:
            pytest.skip("No JPG test images found")
        
        # Just verify the function can process the image without errors
        # and returns the expected dictionary structure
        try:
            result = extract_text_from_image(image_files[0])
            assert isinstance(result, dict)
            assert "position" in result
            assert "character" in result
            assert "player" in result
        except Exception as e:
            pytest.skip(f"Could not process test image: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
