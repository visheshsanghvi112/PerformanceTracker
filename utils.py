from datetime import datetime

# Parse a date string to a datetime object
def parse_date(date_str, fmt='%Y-%m-%d'):
    """
    Parses a date string to a datetime object.
    """
    try:
        return datetime.strptime(date_str, fmt)
    except Exception:
        return None

# Format a datetime object to a string
def format_date(dt, fmt='%Y-%m-%d'):
    """
    Formats a datetime object to a string.
    """
    if dt:
        return dt.strftime(fmt)
    return '' 