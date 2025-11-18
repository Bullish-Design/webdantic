# src/webdantic/exceptions/errors.py
from __future__ import annotations


class WebdanticError(Exception):
    """Base exception for all Webdantic errors."""
    pass


class ConnectionError(WebdanticError):
    """Raised when browser connection fails or is lost."""
    pass


class NavigationError(WebdanticError):
    """Raised when page navigation fails."""
    pass


class SelectorError(WebdanticError):
    """Raised when element selection fails."""
    pass


class TimeoutError(WebdanticError):
    """Raised when an operation times out."""
    pass


class WindowError(WebdanticError):
    """Raised when window operations fail."""
    pass


class TabError(WebdanticError):
    """Raised when tab operations fail."""
    pass