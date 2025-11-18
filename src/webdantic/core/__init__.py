# src/webdantic/core/__init__.py
from __future__ import annotations

from webdantic.core.browser import Browser
from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.core.tab import Tab
from webdantic.core.window import Window

__all__ = [
    "Browser",
    "Page",
    "Selector",
    "Tab",
    "Window",
]