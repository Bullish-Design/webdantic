# tests/test_public_api.py
"""Test public API exports."""
import webdantic


def test_version():
    """Test version is available."""
    assert hasattr(webdantic, "__version__")
    assert isinstance(webdantic.__version__, str)


def test_core_objects_exported():
    """Test core objects are exported."""
    assert hasattr(webdantic, "Browser")
    assert hasattr(webdantic, "Window")
    assert hasattr(webdantic, "Tab")
    assert hasattr(webdantic, "Page")
    assert hasattr(webdantic, "Selector")


def test_config_exported():
    """Test config objects are exported."""
    assert hasattr(webdantic, "BrowserConfig")
    assert hasattr(webdantic, "PageConfig")
    assert hasattr(webdantic, "ScreenshotConfig")


def test_exceptions_exported():
    """Test exceptions are exported."""
    assert hasattr(webdantic, "WebdanticError")
    assert hasattr(webdantic, "ConnectionError")
    assert hasattr(webdantic, "NavigationError")
    assert hasattr(webdantic, "SelectorError")
    assert hasattr(webdantic, "TabError")
    assert hasattr(webdantic, "TimeoutError")
    assert hasattr(webdantic, "WindowError")


def test_all_exports():
    """Test __all__ contains expected exports."""
    expected = {
        "Browser", "Window", "Tab", "Page", "Selector",
        "BrowserConfig", "PageConfig", "ScreenshotConfig",
        "WebdanticError", "ConnectionError", "NavigationError",
        "SelectorError", "TabError", "TimeoutError", "WindowError",
        "__version__",
    }
    assert set(webdantic.__all__) == expected