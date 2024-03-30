"""Constants and configuration."""

from pathlib import Path

VERSION = "0.1.0"
ROOT_DIR = Path(__file__).parent.parent.resolve()

# Directory definitions
ASSETS_DIR = ROOT_DIR / "assets"
DATA_DIR = ROOT_DIR / "data"
TEMPLATES_DIR = ASSETS_DIR / "templates"

LOG_DIR = DATA_DIR / "logs"

TESSERACT_PATH = ROOT_DIR / "Tesseract-OCR" / "tesseract.exe"
