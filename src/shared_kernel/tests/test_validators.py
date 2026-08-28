import pytest
from pydantic import BaseModel
from shared_kernel.interface.validators import SanitizedString

class DummyRequest(BaseModel):
    text: SanitizedString

def test_sanitized_string_strips_html():
    # Arrange
    payload = "<script>alert('xss')</script>Hello <b>World</b>"
    
    # Act
    request = DummyRequest(text=payload)
    
    # Assert
    assert request.text == "Hello World"
    assert "<script>" not in request.text
    assert "<b>" not in request.text

def test_sanitized_string_leaves_plain_text_alone():
    # Arrange
    payload = "Just a normal string with no HTML."
    
    # Act
    request = DummyRequest(text=payload)
    
    # Assert
    assert request.text == payload
