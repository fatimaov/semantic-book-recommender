"""Presentation settings for the Gradio frontend."""

from pathlib import Path


FRONTEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_ROOT.parent
COVER_NOT_FOUND_PATH = FRONTEND_ROOT / "assets" / "cover_not_found.png"
PAGE_SIZE = 16

CATEGORY_CHOICES = [
    "All",
    "Children's Fiction",
    "Children's Nonfiction",
    "Fiction",
    "Nonfiction",
]
TONE_CHOICES = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]
