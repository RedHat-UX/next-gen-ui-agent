"""Default data loading utilities."""

import json

from app.config import DEFAULT_DATA_FILE


def load_default_data():
    """Load default movies data from JSON file."""
    try:
        with open(DEFAULT_DATA_FILE, "r") as f:
            data = json.load(f)
            if data and len(data) > 0:
                print(f"Loaded {len(data)} movies from default data file")
                return data
            else:
                print("Default data file is empty")
                return None
    except FileNotFoundError:
        print(f"Default data file not found: {DEFAULT_DATA_FILE}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing default data file: {e}")
        return None
    except Exception as e:
        print(f"Error loading default data: {e}")
        return None


# Load default data on module import
DEFAULT_DATA = load_default_data()
