"""Configuration settings and constants for NGUI E2E API."""

import os

# Maximum data size in MB (prevents server memory issues)
MAX_DATA_SIZE_MB = 10

# Default data file path
DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "movies_data.json")

# Available movies list for suggestions
AVAILABLE_MOVIES = [
    "Toy Story",
    "The Shawshank Redemption", 
    "The Dark Knight",
    "Inception",
    "The Matrix",
    "Interstellar"
]



