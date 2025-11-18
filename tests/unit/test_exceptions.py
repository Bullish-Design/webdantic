# tests/unit/test_exceptions.py
import pytest
from webdantic.exceptions import (
    ConnectionError,
    NavigationError,
    SelectorError,
    TabError,
    TimeoutError,
    WebdanticError,
    WindowError,
)


def test_exception_hierarchy():
    """Test that all exceptions inherit from WebdanticError."""
    exceptions = [
        ConnectionError,
        NavigationError,
        SelectorError,
        TabError,
        TimeoutError,
        WindowError,
    ]
    
    for exc_class in exceptions:
        assert issubclass(exc_class, WebdanticError)


def test_exception_raising():
    """Test that exceptions can be raised and caught."""
    with pytest.raises(WebdanticError):
        raise ConnectionError("Test error")
    
    with pytest.raises(ConnectionError):
        raise ConnectionError("Test error")