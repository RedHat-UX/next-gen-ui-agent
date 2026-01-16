"""Data source handlers for different input types."""

from .default_data import DEFAULT_DATA, load_default_data
from .filtering import generic_data_filter_agent
from .inline import process_inline_data
from .movies import (
    extract_movie_fields,
    get_movie_data_summary,
    log_movie_data_info,
    validate_movie_data,
)

__all__ = [
    "process_inline_data",
    "generic_data_filter_agent",
    "DEFAULT_DATA",
    "load_default_data",
    "get_movie_data_summary",
    "log_movie_data_info",
    "validate_movie_data",
    "extract_movie_fields",
]
