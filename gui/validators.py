"""
Shared input validation helpers.

Every check returns True/False (never raises) so callers can do:

    if not is_valid_name(head.get()):
        messagebox.showerror("Invalid Input", "Department head name looks invalid.")
        return

Keep validation rules here so every form uses the same definition of a
"valid" name, date, phone number, etc.
"""

import re
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

# Letters, spaces, apostrophes, hyphens and periods only (e.g. "Mary O'Neil", "Dr. J. Smith").
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,79}$")

# Optional leading +, 7-15 digits total, digits may be separated by spaces or hyphens.
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9 \-]{5,14}[0-9]$")

# Department / institution names: letters, digits, spaces and a few common
# punctuation marks (e.g. "R&D", "Computer Science (CS)", "Block A-1").
FREE_TEXT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 &,.\-()/]{1,99}$")


def is_valid_date(value, date_format=DATE_FORMAT):
    """True if value is a real calendar date in the given format."""
    if not value or not isinstance(value, str):
        return False
    try:
        datetime.strptime(value.strip(), date_format)
        return True
    except ValueError:
        return False


def is_not_future_date(value, date_format=DATE_FORMAT):
    """True if value is a valid date that is today or earlier."""
    if not is_valid_date(value, date_format):
        return False
    return datetime.strptime(value.strip(), date_format).date() <= datetime.now().date()


def is_valid_name(value, min_len=2, max_len=80):
    """True for human names: letters, spaces, apostrophes, hyphens, periods."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    return min_len <= len(value) <= max_len and bool(NAME_PATTERN.match(value))


def is_valid_phone(value):
    """True for phone numbers: optional +, 7-15 digits, spaces/hyphens allowed."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    digit_count = sum(ch.isdigit() for ch in value)
    return 7 <= digit_count <= 15 and bool(PHONE_PATTERN.match(value))


def is_valid_free_text(value, min_len=2, max_len=100):
    """True for general text fields (department/institution names, locations, addresses)."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    return min_len <= len(value) <= max_len and bool(FREE_TEXT_PATTERN.match(value))


def is_positive_number(value):
    """True if value parses to a number strictly greater than 0."""
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def is_non_negative_number(value):
    """True if value parses to a number >= 0."""
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False
