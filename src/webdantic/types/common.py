# src/webdantic/types/common.py
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

# Common type aliases
JavaScriptCode = str
CSSSelector = str
XPathSelector = str
TimeoutMilliseconds = int

# Load states
LoadState = Literal["load", "domcontentloaded", "networkidle", "commit"]

# Wait conditions
WaitUntil = Literal["load", "domcontentloaded", "networkidle", "commit"]

class MouseButton(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

class KeyboardModifier(str, Enum):
    ALT = "Alt"
    CONTROL = "Control"
    META = "Meta"
    SHIFT = "Shift"