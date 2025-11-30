#!/usr/bin/env python3
"""
Script to generate sample race standings screenshots for testing.
This creates images that simulate what a race standings screen might look like.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_race_standings_image(
    race_name: str,
    standings: list[tuple[int, str, str]],
    output_path: Path,
) -> None:
    """
    Create a sample race standings image.

    Args:
        race_name: Name of the race
        standings: List of (placement, character_name, user_name) tuples
        output_path: Path to save the image
    """
    # Image dimensions (simulating a game screenshot with race standings on left)
    width = 1920
    height = 1080

    # Create image with dark background
    img = Image.new("RGB", (width, height), color=(30, 30, 40))
    draw = ImageDraw.Draw(img)

    # Use default font (monospace-like for clarity)
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except OSError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Draw title on the left half
    draw.text((50, 30), race_name, fill=(255, 215, 0), font=font_large)

    # Draw standings
    y_start = 100
    line_height = 55

    for placement, character_name, user_name in standings:
        y = y_start + (placement - 1) * line_height

        # Format placement with suffix
        if 11 <= placement <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(placement % 10, "th")

        placement_text = f"{placement}{suffix}"

        # Color based on placement
        if placement == 1:
            color = (255, 215, 0)  # Gold
        elif placement == 2:
            color = (192, 192, 192)  # Silver
        elif placement == 3:
            color = (205, 127, 50)  # Bronze
        else:
            color = (220, 220, 220)  # White

        # Draw placement
        draw.text((50, y), f"{placement_text}", fill=color, font=font_medium)

        # Draw character name
        draw.text((150, y), character_name, fill=(255, 255, 255), font=font_medium)

        # Draw user name
        draw.text((450, y), user_name, fill=(150, 200, 255), font=font_medium)

    # Add some visual elements on the right half (simulating other UI elements)
    # This part will be cropped off
    draw.rectangle([(width // 2 + 50, 50), (width - 50, height - 50)], outline=(80, 80, 80), width=2)
    draw.text(
        (width // 2 + 100, 100),
        "Race Replay & Statistics",
        fill=(100, 100, 100),
        font=font_large,
    )

    # Save the image
    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


def main() -> None:
    """Generate sample race standings images."""
    project_root = Path(__file__).parent.parent
    screenshots_dir = project_root / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # Sample race data based on Uma Musume characters
    races = [
        (
            "Race 1 - Tokyo Derby",
            [
                (1, "Maruzensky", "Kysix"),
                (2, "Haru Urara", "Sebaxd321"),
                (3, "Oguri Cap", "Archer"),
                (4, "Gold Ship", "StarPlayer"),
                (5, "Mejiro McQueen", "Thunder99"),
                (6, "Tokai Teio", "RaceKing"),
                (7, "Special Week", "Lucky7"),
                (8, "Silence Suzuka", "SpeedDemon"),
            ],
        ),
        (
            "Race 2 - Spring Stakes",
            [
                (1, "Rice Shower", "TopRacer"),
                (2, "Symboli Rudolf", "Champion01"),
                (3, "Daiwa Scarlet", "FastRunner"),
                (4, "Vodka", "WinnerX"),
                (5, "Admire Vega", "StarDust"),
                (6, "El Condor Pasa", "FlyHigh"),
                (7, "Grass Wonder", "GreenField"),
                (8, "Seiun Sky", "CloudNine"),
            ],
        ),
        (
            "Race 3 - Champions Cup",
            [
                (1, "Tamamo Cross", "BestPlayer"),
                (2, "Super Creek", "RiverFlow"),
                (3, "Agnes Tachyon", "ScienceGuy"),
                (4, "Narita Brian", "BrianFan"),
                (5, "Air Groove", "SmoothRide"),
                (6, "Agnes Digital", "TechMaster"),
                (7, "Smart Falcon", "WiseBird"),
                (8, "Kitasan Black", "DarkHorse"),
            ],
        ),
    ]

    for i, (race_name, standings) in enumerate(races, start=1):
        output_path = screenshots_dir / f"race{i}_screenshot.png"
        create_race_standings_image(race_name, standings, output_path)

    print(f"\nGenerated {len(races)} sample screenshots in {screenshots_dir}")


if __name__ == "__main__":
    main()
