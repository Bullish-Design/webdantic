# src/webdantic/exceptions/__init__.py
from __future__ import annotations

from webdantic.exceptions.errors import (
    ConnectionError,
    NavigationError,
    SelectorError,
    TabError,
    TimeoutError,
    WebdanticError,
    WindowError,
)

__all__ = [
    "ConnectionError",
    "NavigationError",
    "SelectorError",
    "TabError",
    "TimeoutError",
    "WebdanticError",
    "WindowError",
]