
def regularize_spaces(text: str) -> str:
    """Replace multiple spaces, newlines and tabs with a single space in `text`."""
    return ' '.join(text.split())
