# tests/unit/test_types.py
from webdantic.types import (
    CSSSelector,
    JavaScriptCode,
    KeyboardModifier,
    LoadState,
    MouseButton,
    TimeoutMilliseconds,
    WaitUntil,
    XPathSelector,
)


def test_type_aliases():
    """Test that type aliases are properly defined."""
    selector: CSSSelector = "div.content"
    xpath: XPathSelector = "//div[@class='content']"
    js: JavaScriptCode = "() => document.title"
    timeout: TimeoutMilliseconds = 5000
    
    assert isinstance(selector, str)
    assert isinstance(xpath, str)
    assert isinstance(js, str)
    assert isinstance(timeout, int)


def test_enums():
    """Test enum definitions."""
    assert MouseButton.LEFT.value == "left"
    assert KeyboardModifier.CONTROL.value == "Control"
    
    assert "load" in LoadState.__args__
    assert "networkidle" in WaitUntil.__args__