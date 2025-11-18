# src/webdantic/__init__.py
from __future__ import annotations

from webdantic.config import BrowserConfig, PageConfig, ScreenshotConfig
from webdantic.core import Browser, Page, Selector, Tab, Window
from webdantic.exceptions import (
    ConnectionError,
    NavigationError,
    SelectorError,
    TabError,
    TimeoutError,
    WebdanticError,
    WindowError,
)

__version__ = "0.1.0"

__all__ = [
    # Core objects
    "Browser",
    "Window",
    "Tab",
    "Page",
    "Selector",
    # Configuration
    "BrowserConfig",
    "PageConfig",
    "ScreenshotConfig",
    # Exceptions
    "WebdanticError",
    "ConnectionError",
    "NavigationError",
    "SelectorError",
    "TabError",
    "TimeoutError",
    "WindowError",
    # Version
    "__version__",
]
