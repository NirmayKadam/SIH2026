from typing import Annotated
import nh3
from pydantic import BeforeValidator

def sanitize_html(value: str) -> str:
    """
    Strips all HTML tags from the input string using nh3 (ammonia).
    Used as a Pydantic BeforeValidator to prevent XSS payloads.
    """
    if not isinstance(value, str):
        return value
    return nh3.clean(value, tags=set())

SanitizedString = Annotated[str, BeforeValidator(sanitize_html)]
