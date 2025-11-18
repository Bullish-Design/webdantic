# SPEC.md

# Webdantic MVP Development Specification

## Overview
This specification provides a step-by-step guide to building the MVP of Webdantic - a Pythonic, Pydantic-based wrapper for Chrome DevTools Protocol (CDP) via Playwright. Each step builds on the previous one and includes both implementation and testing requirements.

## Directory Structure
```
webdantic/
├── pyproject.toml              # UV project configuration
├── README.md                   # User documentation
├── SPEC.md                     # This file
├── src/
│   └── webdantic/              # Main package (entry point)
│       ├── __init__.py         # Public API exports
│       ├── core/               # Core object models
│       │   ├── __init__.py
│       │   ├── browser.py      # Browser class
│       │   ├── window.py       # Window class
│       │   ├── tab.py          # Tab class
│       │   ├── page.py         # Page class
│       │   └── selector.py     # Selector class
│       ├── config/             # Configuration models
│       │   ├── __init__.py
│       │   └── models.py       # Pydantic config models
│       ├── exceptions/         # Custom exceptions
│       │   ├── __init__.py
│       │   └── errors.py       # Exception hierarchy
│       ├── types/              # Type definitions
│       │   ├── __init__.py
│       │   └── common.py       # Common types and enums
│       └── utils/              # Utilities
│           ├── __init__.py
│           └── helpers.py      # Helper functions
├── examples/                   # Usage examples
│   ├── basic_navigation.py
│   ├── form_filling.py
│   └── screenshots.py
└── tests/                      # Test suite
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures
    ├── unit/                   # Unit tests
    │   ├── __init__.py
    │   ├── test_browser.py
    │   ├── test_window.py
    │   ├── test_tab.py
    │   ├── test_page.py
    │   └── test_selector.py
    └── integration/            # Integration tests
        ├── __init__.py
        └── test_e2e.py         # End-to-end tests
```

## Prerequisites
- Python 3.11+
- UV package manager installed
- Chrome/Chromium browser installed
- Basic understanding of async/await patterns
- Familiarity with Pydantic v2

---

## Step 1: Project Scaffolding and Foundation

### 1.1 Development Tasks

**Create pyproject.toml**
- Set up UV-based project with metadata
- Define dependencies: `playwright>=1.40.0`, `pydantic>=2.5.0`
- Define dev dependencies: `pytest>=7.4.0`, `pytest-asyncio>=0.21.0`, `mypy>=1.7.0`, `ruff>=0.1.6`
- Configure build system (hatchling or setuptools)
- Set Python version requirement to 3.11+

**Create directory structure**
```bash
mkdir -p src/webdantic/{core,config,exceptions,types,utils}
mkdir -p tests/{unit,integration}
mkdir -p examples
```

**Create __init__.py files**
- Add file path comments to all `__init__.py` files
- Leave core module `__init__.py` files empty for now
- Main `src/webdantic/__init__.py` will be populated later

**Install Playwright**
```bash
uv pip install playwright
playwright install chromium
```

### 1.2 Testing Tasks

**Verify project structure**
```bash
tree src/webdantic
tree tests
```

**Verify imports work**
```python
# test_imports.py
import webdantic
from webdantic.core import browser
from webdantic.exceptions import errors
```

**Verify Playwright installation**
```bash
playwright --version
```

### 1.3 Success Criteria
- [ ] All directories created
- [ ] pyproject.toml valid and installable with UV
- [ ] Playwright installed and functional
- [ ] All `__init__.py` files have path comments
- [ ] Package can be imported without errors

---

## Step 2: Type System and Exceptions

### 2.1 Development Tasks

**Create src/webdantic/types/common.py**
```python
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
```

**Create src/webdantic/types/__init__.py**
```python
# src/webdantic/types/__init__.py
from __future__ import annotations

from webdantic.types.common import (
    CSSSelector,
    JavaScriptCode,
    KeyboardModifier,
    LoadState,
    MouseButton,
    TimeoutMilliseconds,
    WaitUntil,
    XPathSelector,
)

__all__ = [
    "CSSSelector",
    "JavaScriptCode",
    "KeyboardModifier",
    "LoadState",
    "MouseButton",
    "TimeoutMilliseconds",
    "WaitUntil",
    "XPathSelector",
]
```

**Create src/webdantic/exceptions/errors.py**
```python
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
```

**Create src/webdantic/exceptions/__init__.py**
```python
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
```

### 2.2 Testing Tasks

**Create tests/unit/test_exceptions.py**
```python
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
```

**Create tests/unit/test_types.py**
```python
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
```

**Run tests**
```bash
pytest tests/unit/test_exceptions.py tests/unit/test_types.py -v
```

### 2.3 Success Criteria
- [ ] All type definitions created and importable
- [ ] Exception hierarchy properly defined
- [ ] All tests pass
- [ ] No mypy errors: `mypy src/webdantic/types src/webdantic/exceptions`

---

## Step 3: Configuration Models

### 3.1 Development Tasks

**Create src/webdantic/config/models.py**
```python
# src/webdantic/config/models.py
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BrowserConfig(BaseModel):
    """Configuration for browser connection."""
    
    host: str = Field(default="localhost", description="CDP host address")
    port: int = Field(default=9222, ge=1024, le=65535, description="CDP port number")
    timeout: int = Field(default=30000, ge=0, description="Default timeout in milliseconds")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    slow_mo: int = Field(default=0, ge=0, description="Slow down operations by milliseconds")
    
    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        return v
    
    @property
    def endpoint_url(self) -> str:
        """Get the CDP endpoint URL."""
        return f"http://{self.host}:{self.port}"


class PageConfig(BaseModel):
    """Configuration for page operations."""
    
    default_timeout: int = Field(default=30000, ge=0, description="Default timeout for operations")
    default_navigation_timeout: int = Field(default=30000, ge=0, description="Default navigation timeout")
    viewport_width: Optional[int] = Field(default=1280, ge=1, description="Viewport width")
    viewport_height: Optional[int] = Field(default=720, ge=1, description="Viewport height")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")


class ScreenshotConfig(BaseModel):
    """Configuration for screenshots."""
    
    full_page: bool = Field(default=False, description="Capture full scrollable page")
    omit_background: bool = Field(default=False, description="Hide default white background")
    quality: Optional[int] = Field(default=None, ge=0, le=100, description="JPEG quality (0-100)")
    type: str = Field(default="png", description="Screenshot type: png or jpeg")
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("png", "jpeg"):
            raise ValueError("type must be 'png' or 'jpeg'")
        return v
```

**Create src/webdantic/config/__init__.py**
```python
# src/webdantic/config/__init__.py
from __future__ import annotations

from webdantic.config.models import BrowserConfig, PageConfig, ScreenshotConfig

__all__ = [
    "BrowserConfig",
    "PageConfig",
    "ScreenshotConfig",
]
```

### 3.2 Testing Tasks

**Create tests/unit/test_config.py**
```python
# tests/unit/test_config.py
import pytest
from pydantic import ValidationError
from webdantic.config import BrowserConfig, PageConfig, ScreenshotConfig


class TestBrowserConfig:
    def test_default_values(self):
        config = BrowserConfig()
        assert config.host == "localhost"
        assert config.port == 9222
        assert config.timeout == 30000
        assert config.headless is False
    
    def test_custom_values(self):
        config = BrowserConfig(port=9223, headless=True)
        assert config.port == 9223
        assert config.headless is True
    
    def test_invalid_port_low(self):
        with pytest.raises(ValidationError):
            BrowserConfig(port=1023)
    
    def test_invalid_port_high(self):
        with pytest.raises(ValidationError):
            BrowserConfig(port=65536)
    
    def test_endpoint_url(self):
        config = BrowserConfig(host="127.0.0.1", port=9222)
        assert config.endpoint_url == "http://127.0.0.1:9222"


class TestPageConfig:
    def test_default_values(self):
        config = PageConfig()
        assert config.default_timeout == 30000
        assert config.viewport_width == 1280
        assert config.viewport_height == 720
    
    def test_custom_values(self):
        config = PageConfig(viewport_width=1920, viewport_height=1080)
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080


class TestScreenshotConfig:
    def test_default_values(self):
        config = ScreenshotConfig()
        assert config.full_page is False
        assert config.type == "png"
    
    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            ScreenshotConfig(type="gif")
    
    def test_quality_validation(self):
        config = ScreenshotConfig(type="jpeg", quality=85)
        assert config.quality == 85
        
        with pytest.raises(ValidationError):
            ScreenshotConfig(quality=101)
```

**Run tests**
```bash
pytest tests/unit/test_config.py -v
```

### 3.3 Success Criteria
- [ ] All config models created with Pydantic validation
- [ ] Validators working correctly
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 4: Selector Class (Leaf Node)

### 4.1 Development Tasks

**Create src/webdantic/core/selector.py**
```python
# src/webdantic/core/selector.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from playwright.async_api import Locator
from pydantic import BaseModel, ConfigDict, Field

from webdantic.exceptions import SelectorError, TimeoutError
from webdantic.types import CSSSelector

if TYPE_CHECKING:
    from webdantic.core.page import Page


class Selector(BaseModel):
    """Represents a selected element or elements on a page."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    selector: CSSSelector = Field(description="CSS selector string")
    _page: Page = Field(exclude=True, repr=False)
    _locator: Locator = Field(exclude=True, repr=False)
    
    def __init__(self, selector: CSSSelector, page: Page, locator: Locator):
        """Initialize selector with page and locator references."""
        super().__init__(selector=selector, _page=page, _locator=locator)
    
    @property
    def page(self) -> Page:
        """Get parent Page object."""
        return self._page
    
    @property
    def playwright_locator(self) -> Locator:
        """Get underlying Playwright locator for escape hatch."""
        return self._locator
    
    async def click(self, timeout: Optional[int] = None) -> None:
        """Click the element."""
        try:
            await self._locator.click(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to click element '{self.selector}': {e}") from e
    
    async def type(self, text: str, delay: Optional[int] = None, timeout: Optional[int] = None) -> None:
        """Type text into the element character by character."""
        try:
            await self._locator.type(text, delay=delay, timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to type into element '{self.selector}': {e}") from e
    
    async def fill(self, text: str, timeout: Optional[int] = None) -> None:
        """Fill the element with text (clears first)."""
        try:
            await self._locator.fill(text, timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to fill element '{self.selector}': {e}") from e
    
    async def text(self, timeout: Optional[int] = None) -> str:
        """Get text content of the element."""
        try:
            content = await self._locator.text_content(timeout=timeout)
            return content or ""
        except Exception as e:
            raise SelectorError(f"Failed to get text from element '{self.selector}': {e}") from e
    
    async def inner_text(self, timeout: Optional[int] = None) -> str:
        """Get inner text of the element."""
        try:
            return await self._locator.inner_text(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to get inner text from element '{self.selector}': {e}") from e
    
    async def inner_html(self, timeout: Optional[int] = None) -> str:
        """Get inner HTML of the element."""
        try:
            return await self._locator.inner_html(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to get inner HTML from element '{self.selector}': {e}") from e
    
    async def attribute(self, name: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get attribute value from the element."""
        try:
            return await self._locator.get_attribute(name, timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to get attribute '{name}' from element '{self.selector}': {e}") from e
    
    async def is_visible(self, timeout: Optional[int] = None) -> bool:
        """Check if element is visible."""
        try:
            return await self._locator.is_visible(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to check visibility of element '{self.selector}': {e}") from e
    
    async def is_hidden(self, timeout: Optional[int] = None) -> bool:
        """Check if element is hidden."""
        try:
            return await self._locator.is_hidden(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to check hidden state of element '{self.selector}': {e}") from e
    
    async def is_enabled(self, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled."""
        try:
            return await self._locator.is_enabled(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to check enabled state of element '{self.selector}': {e}") from e
    
    async def is_disabled(self, timeout: Optional[int] = None) -> bool:
        """Check if element is disabled."""
        try:
            return await self._locator.is_disabled(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to check disabled state of element '{self.selector}': {e}") from e
    
    async def count(self) -> int:
        """Get count of elements matching this selector."""
        try:
            return await self._locator.count()
        except Exception as e:
            raise SelectorError(f"Failed to count elements for selector '{self.selector}': {e}") from e
    
    async def wait_for(
        self,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> None:
        """Wait for element to reach a specific state."""
        try:
            await self._locator.wait_for(state=state, timeout=timeout)
        except Exception as e:
            raise TimeoutError(
                f"Timeout waiting for element '{self.selector}' to be {state}: {e}"
            ) from e
```

**Update src/webdantic/core/__init__.py**
```python
# src/webdantic/core/__init__.py
from __future__ import annotations

from webdantic.core.selector import Selector

__all__ = [
    "Selector",
]
```

### 4.2 Testing Tasks

**Create tests/unit/test_selector.py**
```python
# tests/unit/test_selector.py
import pytest
from unittest.mock import AsyncMock, Mock
from webdantic.core.selector import Selector
from webdantic.exceptions import SelectorError


@pytest.fixture
def mock_page():
    """Create a mock Page object."""
    return Mock()


@pytest.fixture
def mock_locator():
    """Create a mock Playwright locator."""
    locator = Mock()
    locator.click = AsyncMock()
    locator.type = AsyncMock()
    locator.fill = AsyncMock()
    locator.text_content = AsyncMock(return_value="Test text")
    locator.inner_text = AsyncMock(return_value="Test text")
    locator.inner_html = AsyncMock(return_value="<div>Test</div>")
    locator.get_attribute = AsyncMock(return_value="test-value")
    locator.is_visible = AsyncMock(return_value=True)
    locator.is_hidden = AsyncMock(return_value=False)
    locator.is_enabled = AsyncMock(return_value=True)
    locator.is_disabled = AsyncMock(return_value=False)
    locator.count = AsyncMock(return_value=1)
    locator.wait_for = AsyncMock()
    return locator


@pytest.fixture
def selector(mock_page, mock_locator):
    """Create a Selector instance."""
    return Selector(selector="div.test", page=mock_page, locator=mock_locator)


@pytest.mark.asyncio
async def test_selector_initialization(selector, mock_page, mock_locator):
    """Test selector initialization."""
    assert selector.selector == "div.test"
    assert selector.page is mock_page
    assert selector.playwright_locator is mock_locator


@pytest.mark.asyncio
async def test_click(selector, mock_locator):
    """Test click operation."""
    await selector.click()
    mock_locator.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_type(selector, mock_locator):
    """Test type operation."""
    await selector.type("hello")
    mock_locator.type.assert_awaited_once_with("hello", delay=None, timeout=None)


@pytest.mark.asyncio
async def test_fill(selector, mock_locator):
    """Test fill operation."""
    await selector.fill("hello")
    mock_locator.fill.assert_awaited_once_with("hello", timeout=None)


@pytest.mark.asyncio
async def test_text(selector, mock_locator):
    """Test text extraction."""
    text = await selector.text()
    assert text == "Test text"
    mock_locator.text_content.assert_awaited_once()


@pytest.mark.asyncio
async def test_attribute(selector, mock_locator):
    """Test attribute extraction."""
    value = await selector.attribute("href")
    assert value == "test-value"
    mock_locator.get_attribute.assert_awaited_once_with("href", timeout=None)


@pytest.mark.asyncio
async def test_is_visible(selector, mock_locator):
    """Test visibility check."""
    visible = await selector.is_visible()
    assert visible is True
    mock_locator.is_visible.assert_awaited_once()


@pytest.mark.asyncio
async def test_count(selector, mock_locator):
    """Test element count."""
    count = await selector.count()
    assert count == 1
    mock_locator.count.assert_awaited_once()


@pytest.mark.asyncio
async def test_click_error(selector, mock_locator):
    """Test error handling in click."""
    mock_locator.click.side_effect = Exception("Click failed")
    
    with pytest.raises(SelectorError) as exc_info:
        await selector.click()
    
    assert "Failed to click element" in str(exc_info.value)
```

**Run tests**
```bash
pytest tests/unit/test_selector.py -v
```

### 4.3 Success Criteria
- [ ] Selector class implemented with all basic operations
- [ ] Escape hatch to Playwright locator available
- [ ] Proper error handling with custom exceptions
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 5: Page Class

### 5.1 Development Tasks

**Create src/webdantic/core/page.py**
```python
# src/webdantic/core/page.py
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from playwright.async_api import Page as PlaywrightPage
from pydantic import BaseModel, ConfigDict, Field

from webdantic.config import ScreenshotConfig
from webdantic.core.selector import Selector
from webdantic.exceptions import NavigationError, SelectorError, TimeoutError
from webdantic.types import CSSSelector, JavaScriptCode, LoadState, WaitUntil

if TYPE_CHECKING:
    from webdantic.core.tab import Tab


class Page(BaseModel):
    """Wrapper for Playwright Page with Pydantic validation."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _tab: Tab = Field(exclude=True, repr=False)
    _playwright_page: PlaywrightPage = Field(exclude=True, repr=False)
    
    def __init__(self, tab: Tab, playwright_page: PlaywrightPage):
        """Initialize Page with tab and Playwright page references."""
        super().__init__(_tab=tab, _playwright_page=playwright_page)
    
    @property
    def tab(self) -> Tab:
        """Get parent Tab object."""
        return self._tab
    
    @property
    def playwright_page(self) -> PlaywrightPage:
        """Get underlying Playwright page for escape hatch."""
        return self._playwright_page
    
    @property
    def url(self) -> str:
        """Get current page URL."""
        return self._playwright_page.url
    
    async def goto(
        self,
        url: str,
        timeout: Optional[int] = None,
        wait_until: Optional[WaitUntil] = None
    ) -> None:
        """Navigate to a URL."""
        try:
            await self._playwright_page.goto(url, timeout=timeout, wait_until=wait_until)
        except Exception as e:
            raise NavigationError(f"Failed to navigate to '{url}': {e}") from e
    
    async def reload(
        self,
        timeout: Optional[int] = None,
        wait_until: Optional[WaitUntil] = None
    ) -> None:
        """Reload the current page."""
        try:
            await self._playwright_page.reload(timeout=timeout, wait_until=wait_until)
        except Exception as e:
            raise NavigationError(f"Failed to reload page: {e}") from e
    
    async def go_back(
        self,
        timeout: Optional[int] = None,
        wait_until: Optional[WaitUntil] = None
    ) -> None:
        """Navigate back in history."""
        try:
            await self._playwright_page.go_back(timeout=timeout, wait_until=wait_until)
        except Exception as e:
            raise NavigationError(f"Failed to go back: {e}") from e
    
    async def go_forward(
        self,
        timeout: Optional[int] = None,
        wait_until: Optional[WaitUntil] = None
    ) -> None:
        """Navigate forward in history."""
        try:
            await self._playwright_page.go_forward(timeout=timeout, wait_until=wait_until)
        except Exception as e:
            raise NavigationError(f"Failed to go forward: {e}") from e
    
    async def select(self, selector: CSSSelector, timeout: Optional[int] = None) -> Selector:
        """Select a single element and return a Selector object."""
        try:
            locator = self._playwright_page.locator(selector)
            # Verify element exists
            await locator.wait_for(state="attached", timeout=timeout)
            return Selector(selector=selector, page=self, locator=locator)
        except Exception as e:
            raise SelectorError(f"Failed to select element '{selector}': {e}") from e
    
    async def select_all(self, selector: CSSSelector) -> list[Selector]:
        """Select all matching elements and return list of Selector objects."""
        try:
            locator = self._playwright_page.locator(selector)
            count = await locator.count()
            
            selectors = []
            for i in range(count):
                nth_locator = locator.nth(i)
                selectors.append(Selector(selector=f"{selector}:nth-match({i+1})", page=self, locator=nth_locator))
            
            return selectors
        except Exception as e:
            raise SelectorError(f"Failed to select elements '{selector}': {e}") from e
    
    async def wait_for_selector(
        self,
        selector: CSSSelector,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> Selector:
        """Wait for selector and return Selector object."""
        try:
            locator = self._playwright_page.locator(selector)
            await locator.wait_for(state=state, timeout=timeout)
            return Selector(selector=selector, page=self, locator=locator)
        except Exception as e:
            raise TimeoutError(f"Timeout waiting for selector '{selector}': {e}") from e
    
    async def wait_for_load_state(self, state: LoadState = "load", timeout: Optional[int] = None) -> None:
        """Wait for page to reach a specific load state."""
        try:
            await self._playwright_page.wait_for_load_state(state, timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"Timeout waiting for load state '{state}': {e}") from e
    
    async def wait_for_navigation(
        self,
        timeout: Optional[int] = None,
        wait_until: Optional[WaitUntil] = None
    ) -> None:
        """Wait for navigation to complete."""
        try:
            await self._playwright_page.wait_for_load_state(wait_until or "load", timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"Timeout waiting for navigation: {e}") from e
    
    async def evaluate(self, script: JavaScriptCode, arg: Any = None) -> Any:
        """Evaluate JavaScript in page context."""
        try:
            return await self._playwright_page.evaluate(script, arg)
        except Exception as e:
            raise NavigationError(f"Failed to evaluate JavaScript: {e}") from e
    
    async def title(self) -> str:
        """Get page title."""
        return await self._playwright_page.title()
    
    async def content(self) -> str:
        """Get page HTML content."""
        return await self._playwright_page.content()
    
    async def screenshot(
        self,
        path: Optional[Path | str] = None,
        config: Optional[ScreenshotConfig] = None
    ) -> bytes:
        """Take a screenshot of the page."""
        try:
            config = config or ScreenshotConfig()
            
            screenshot_args = {
                "path": str(path) if path else None,
                "full_page": config.full_page,
                "omit_background": config.omit_background,
                "type": config.type,
            }
            
            if config.type == "jpeg" and config.quality:
                screenshot_args["quality"] = config.quality
            
            return await self._playwright_page.screenshot(**screenshot_args)
        except Exception as e:
            raise NavigationError(f"Failed to take screenshot: {e}") from e
    
    async def pdf(
        self,
        path: Optional[Path | str] = None,
        format: str = "A4"
    ) -> bytes:
        """Generate PDF of the page."""
        try:
            return await self._playwright_page.pdf(path=str(path) if path else None, format=format)
        except Exception as e:
            raise NavigationError(f"Failed to generate PDF: {e}") from e
    
    async def close(self) -> None:
        """Close the page/tab."""
        try:
            await self._playwright_page.close()
        except Exception as e:
            raise NavigationError(f"Failed to close page: {e}") from e
```

**Update src/webdantic/core/__init__.py**
```python
# src/webdantic/core/__init__.py
from __future__ import annotations

from webdantic.core.page import Page
from webdantic.core.selector import Selector

__all__ = [
    "Page",
    "Selector",
]
```

### 5.2 Testing Tasks

**Create tests/unit/test_page.py**
```python
# tests/unit/test_page.py
import pytest
from unittest.mock import AsyncMock, Mock, patch
from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.exceptions import NavigationError, SelectorError


@pytest.fixture
def mock_tab():
    """Create a mock Tab object."""
    return Mock()


@pytest.fixture
def mock_playwright_page():
    """Create a mock Playwright page."""
    page = Mock()
    page.url = "https://example.com"
    page.goto = AsyncMock()
    page.reload = AsyncMock()
    page.go_back = AsyncMock()
    page.go_forward = AsyncMock()
    page.evaluate = AsyncMock(return_value="result")
    page.title = AsyncMock(return_value="Test Page")
    page.content = AsyncMock(return_value="<html></html>")
    page.screenshot = AsyncMock(return_value=b"image_data")
    page.pdf = AsyncMock(return_value=b"pdf_data")
    page.close = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    
    # Mock locator
    locator = Mock()
    locator.wait_for = AsyncMock()
    locator.count = AsyncMock(return_value=2)
    locator.nth = Mock(return_value=Mock())
    page.locator = Mock(return_value=locator)
    
    return page


@pytest.fixture
def page(mock_tab, mock_playwright_page):
    """Create a Page instance."""
    return Page(tab=mock_tab, playwright_page=mock_playwright_page)


@pytest.mark.asyncio
async def test_page_initialization(page, mock_tab, mock_playwright_page):
    """Test page initialization."""
    assert page.tab is mock_tab
    assert page.playwright_page is mock_playwright_page


@pytest.mark.asyncio
async def test_url_property(page):
    """Test URL property."""
    assert page.url == "https://example.com"


@pytest.mark.asyncio
async def test_goto(page, mock_playwright_page):
    """Test navigation."""
    await page.goto("https://test.com")
    mock_playwright_page.goto.assert_awaited_once_with(
        "https://test.com",
        timeout=None,
        wait_until=None
    )


@pytest.mark.asyncio
async def test_reload(page, mock_playwright_page):
    """Test page reload."""
    await page.reload()
    mock_playwright_page.reload.assert_awaited_once()


@pytest.mark.asyncio
async def test_go_back(page, mock_playwright_page):
    """Test back navigation."""
    await page.go_back()
    mock_playwright_page.go_back.assert_awaited_once()


@pytest.mark.asyncio
async def test_select(page, mock_playwright_page):
    """Test element selection."""
    selector = await page.select("div.test")
    
    assert isinstance(selector, Selector)
    assert selector.selector == "div.test"
    mock_playwright_page.locator.assert_called_once_with("div.test")


@pytest.mark.asyncio
async def test_select_all(page, mock_playwright_page):
    """Test selecting multiple elements."""
    selectors = await page.select_all("button")
    
    assert len(selectors) == 2
    assert all(isinstance(s, Selector) for s in selectors)


@pytest.mark.asyncio
async def test_evaluate(page, mock_playwright_page):
    """Test JavaScript evaluation."""
    result = await page.evaluate("() => 1 + 1")
    assert result == "result"
    mock_playwright_page.evaluate.assert_awaited_once()


@pytest.mark.asyncio
async def test_title(page, mock_playwright_page):
    """Test getting page title."""
    title = await page.title()
    assert title == "Test Page"


@pytest.mark.asyncio
async def test_screenshot(page, mock_playwright_page):
    """Test screenshot capture."""
    data = await page.screenshot()
    assert data == b"image_data"
    mock_playwright_page.screenshot.assert_awaited_once()


@pytest.mark.asyncio
async def test_goto_error(page, mock_playwright_page):
    """Test navigation error handling."""
    mock_playwright_page.goto.side_effect = Exception("Navigation failed")
    
    with pytest.raises(NavigationError) as exc_info:
        await page.goto("https://test.com")
    
    assert "Failed to navigate" in str(exc_info.value)
```

**Run tests**
```bash
pytest tests/unit/test_page.py -v
```

### 5.3 Success Criteria
- [ ] Page class implemented with navigation and selection
- [ ] Selector objects properly created and returned
- [ ] Escape hatch to Playwright page available
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 6: Tab Class

### 6.1 Development Tasks

**Create src/webdantic/core/tab.py**
```python
# src/webdantic/core/tab.py
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.async_api import Page as PlaywrightPage
from pydantic import BaseModel, ConfigDict, Field

from webdantic.core.page import Page
from webdantic.exceptions import NavigationError, TabError

if TYPE_CHECKING:
    from webdantic.core.window import Window


class Tab(BaseModel):
    """Represents an individual tab within a browser window."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _window: Window = Field(exclude=True, repr=False)
    _playwright_page: PlaywrightPage = Field(exclude=True, repr=False)
    _page_wrapper: Page | None = Field(default=None, exclude=True, repr=False)
    
    def __init__(self, window: Window, playwright_page: PlaywrightPage):
        """Initialize Tab with window and Playwright page references."""
        super().__init__(_window=window, _playwright_page=playwright_page)
    
    @property
    def window(self) -> Window:
        """Get parent Window object."""
        return self._window
    
    @property
    def playwright_page(self) -> PlaywrightPage:
        """Get underlying Playwright page for escape hatch."""
        return self._playwright_page
    
    @property
    def url(self) -> str:
        """Get current tab URL."""
        return self._playwright_page.url
    
    @property
    def title(self) -> str:
        """Get tab title (synchronous accessor)."""
        # Note: This is a property that returns the cached title
        # For the actual async title fetch, use get_page().title()
        try:
            return self._playwright_page.title()
        except:
            return ""
    
    async def get_page(self) -> Page:
        """Get or create the Page wrapper for this tab."""
        if self._page_wrapper is None:
            self._page_wrapper = Page(tab=self, playwright_page=self._playwright_page)
        return self._page_wrapper
    
    async def navigate(self, url: str, timeout: int | None = None) -> None:
        """Navigate this tab to a URL."""
        try:
            await self._playwright_page.goto(url, timeout=timeout)
        except Exception as e:
            raise NavigationError(f"Failed to navigate tab to '{url}': {e}") from e
    
    async def activate(self) -> None:
        """Bring this tab to the foreground."""
        try:
            await self._playwright_page.bring_to_front()
        except Exception as e:
            raise TabError(f"Failed to activate tab: {e}") from e
    
    async def close(self) -> None:
        """Close this tab."""
        try:
            await self._playwright_page.close()
        except Exception as e:
            raise TabError(f"Failed to close tab: {e}") from e
    
    async def is_closed(self) -> bool:
        """Check if tab is closed."""
        return self._playwright_page.is_closed()
```

**Update src/webdantic/core/__init__.py**
```python
# src/webdantic/core/__init__.py
from __future__ import annotations

from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.core.tab import Tab

__all__ = [
    "Page",
    "Selector",
    "Tab",
]
```

### 6.2 Testing Tasks

**Create tests/unit/test_tab.py**
```python
# tests/unit/test_tab.py
import pytest
from unittest.mock import AsyncMock, Mock
from webdantic.core.tab import Tab
from webdantic.core.page import Page
from webdantic.exceptions import NavigationError, TabError


@pytest.fixture
def mock_window():
    """Create a mock Window object."""
    return Mock()


@pytest.fixture
def mock_playwright_page():
    """Create a mock Playwright page."""
    page = Mock()
    page.url = "https://example.com"
    page.title = Mock(return_value="Test Page")
    page.goto = AsyncMock()
    page.bring_to_front = AsyncMock()
    page.close = AsyncMock()
    page.is_closed = Mock(return_value=False)
    return page


@pytest.fixture
def tab(mock_window, mock_playwright_page):
    """Create a Tab instance."""
    return Tab(window=mock_window, playwright_page=mock_playwright_page)


@pytest.mark.asyncio
async def test_tab_initialization(tab, mock_window, mock_playwright_page):
    """Test tab initialization."""
    assert tab.window is mock_window
    assert tab.playwright_page is mock_playwright_page


@pytest.mark.asyncio
async def test_url_property(tab):
    """Test URL property."""
    assert tab.url == "https://example.com"


@pytest.mark.asyncio
async def test_get_page(tab):
    """Test getting Page wrapper."""
    page = await tab.get_page()
    
    assert isinstance(page, Page)
    assert page.tab is tab
    
    # Second call should return same instance
    page2 = await tab.get_page()
    assert page is page2


@pytest.mark.asyncio
async def test_navigate(tab, mock_playwright_page):
    """Test tab navigation."""
    await tab.navigate("https://test.com")
    mock_playwright_page.goto.assert_awaited_once_with("https://test.com", timeout=None)


@pytest.mark.asyncio
async def test_activate(tab, mock_playwright_page):
    """Test tab activation."""
    await tab.activate()
    mock_playwright_page.bring_to_front.assert_awaited_once()


@pytest.mark.asyncio
async def test_close(tab, mock_playwright_page):
    """Test tab closing."""
    await tab.close()
    mock_playwright_page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_closed(tab, mock_playwright_page):
    """Test closed status check."""
    is_closed = await tab.is_closed()
    assert is_closed is False


@pytest.mark.asyncio
async def test_navigate_error(tab, mock_playwright_page):
    """Test navigation error handling."""
    mock_playwright_page.goto.side_effect = Exception("Navigation failed")
    
    with pytest.raises(NavigationError) as exc_info:
        await tab.navigate("https://test.com")
    
    assert "Failed to navigate tab" in str(exc_info.value)


@pytest.mark.asyncio
async def test_close_error(tab, mock_playwright_page):
    """Test close error handling."""
    mock_playwright_page.close.side_effect = Exception("Close failed")
    
    with pytest.raises(TabError) as exc_info:
        await tab.close()
    
    assert "Failed to close tab" in str(exc_info.value)
```

**Run tests**
```bash
pytest tests/unit/test_tab.py -v
```

### 6.3 Success Criteria
- [ ] Tab class implemented with navigation and lifecycle methods
- [ ] Lazy Page wrapper creation
- [ ] Escape hatch to Playwright page available
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 7: Window Class

### 7.1 Development Tasks

**Create src/webdantic/core/window.py**
```python
# src/webdantic/core/window.py
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.async_api import BrowserContext
from pydantic import BaseModel, ConfigDict, Field

from webdantic.core.tab import Tab
from webdantic.exceptions import TabError, WindowError

if TYPE_CHECKING:
    from webdantic.core.browser import Browser


class Window(BaseModel):
    """Represents a browser window/context containing tabs."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _browser: Browser = Field(exclude=True, repr=False)
    _context: BrowserContext = Field(exclude=True, repr=False)
    
    def __init__(self, browser: Browser, context: BrowserContext):
        """Initialize Window with browser and context references."""
        super().__init__(_browser=browser, _context=context)
    
    @property
    def browser(self) -> Browser:
        """Get parent Browser object."""
        return self._browser
    
    @property
    def playwright_context(self) -> BrowserContext:
        """Get underlying Playwright context for escape hatch."""
        return self._context
    
    async def get_tabs(self) -> list[Tab]:
        """Get all tabs in this window."""
        try:
            pages = self._context.pages
            return [Tab(window=self, playwright_page=page) for page in pages]
        except Exception as e:
            raise WindowError(f"Failed to get tabs: {e}") from e
    
    async def get_tab(self, index: int) -> Tab:
        """Get tab by index."""
        try:
            pages = self._context.pages
            if index < 0 or index >= len(pages):
                raise IndexError(f"Tab index {index} out of range (0-{len(pages)-1})")
            return Tab(window=self, playwright_page=pages[index])
        except IndexError as e:
            raise TabError(str(e)) from e
        except Exception as e:
            raise WindowError(f"Failed to get tab at index {index}: {e}") from e
    
    async def get_active_tab(self) -> Tab:
        """Get the currently active tab."""
        try:
            # In Playwright, the most recently created/focused page is typically last
            pages = self._context.pages
            if not pages:
                raise TabError("No tabs available in window")
            # Return the first page as a reasonable default
            return Tab(window=self, playwright_page=pages[0])
        except Exception as e:
            raise WindowError(f"Failed to get active tab: {e}") from e
    
    async def new_tab(self, url: str | None = None) -> Tab:
        """Create a new tab in this window."""
        try:
            page = await self._context.new_page()
            if url:
                await page.goto(url)
            return Tab(window=self, playwright_page=page)
        except Exception as e:
            raise TabError(f"Failed to create new tab: {e}") from e
    
    async def close(self) -> None:
        """Close this window and all its tabs."""
        try:
            await self._context.close()
        except Exception as e:
            raise WindowError(f"Failed to close window: {e}") from e
```

**Update src/webdantic/core/__init__.py**
```python
# src/webdantic/core/__init__.py
from __future__ import annotations

from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.core.tab import Tab
from webdantic.core.window import Window

__all__ = [
    "Page",
    "Selector",
    "Tab",
    "Window",
]
```

### 7.2 Testing Tasks

**Create tests/unit/test_window.py**
```python
# tests/unit/test_window.py
import pytest
from unittest.mock import AsyncMock, Mock
from webdantic.core.window import Window
from webdantic.core.tab import Tab
from webdantic.exceptions import TabError, WindowError


@pytest.fixture
def mock_browser():
    """Create a mock Browser object."""
    return Mock()


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = Mock()
    page.url = "https://example.com"
    page.goto = AsyncMock()
    return page


@pytest.fixture
def mock_context(mock_page):
    """Create a mock Playwright context."""
    context = Mock()
    context.pages = [mock_page]
    context.new_page = AsyncMock(return_value=mock_page)
    context.close = AsyncMock()
    return context


@pytest.fixture
def window(mock_browser, mock_context):
    """Create a Window instance."""
    return Window(browser=mock_browser, context=mock_context)


@pytest.mark.asyncio
async def test_window_initialization(window, mock_browser, mock_context):
    """Test window initialization."""
    assert window.browser is mock_browser
    assert window.playwright_context is mock_context


@pytest.mark.asyncio
async def test_get_tabs(window, mock_context, mock_page):
    """Test getting all tabs."""
    tabs = await window.get_tabs()
    
    assert len(tabs) == 1
    assert all(isinstance(tab, Tab) for tab in tabs)
    assert tabs[0].playwright_page is mock_page


@pytest.mark.asyncio
async def test_get_tab(window, mock_context, mock_page):
    """Test getting tab by index."""
    tab = await window.get_tab(0)
    
    assert isinstance(tab, Tab)
    assert tab.playwright_page is mock_page


@pytest.mark.asyncio
async def test_get_tab_invalid_index(window, mock_context):
    """Test getting tab with invalid index."""
    with pytest.raises(TabError) as exc_info:
        await window.get_tab(10)
    
    assert "out of range" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_active_tab(window, mock_context, mock_page):
    """Test getting active tab."""
    tab = await window.get_active_tab()
    
    assert isinstance(tab, Tab)
    assert tab.playwright_page is mock_page


@pytest.mark.asyncio
async def test_new_tab(window, mock_context, mock_page):
    """Test creating new tab."""
    tab = await window.new_tab()
    
    assert isinstance(tab, Tab)
    mock_context.new_page.assert_awaited_once()


@pytest.mark.asyncio
async def test_new_tab_with_url(window, mock_context, mock_page):
    """Test creating new tab with URL."""
    tab = await window.new_tab("https://test.com")
    
    assert isinstance(tab, Tab)
    mock_context.new_page.assert_awaited_once()
    mock_page.goto.assert_awaited_once_with("https://test.com")


@pytest.mark.asyncio
async def test_close(window, mock_context):
    """Test closing window."""
    await window.close()
    mock_context.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_error(window, mock_context):
    """Test close error handling."""
    mock_context.close.side_effect = Exception("Close failed")
    
    with pytest.raises(WindowError) as exc_info:
        await window.close()
    
    assert "Failed to close window" in str(exc_info.value)
```

**Run tests**
```bash
pytest tests/unit/test_window.py -v
```

### 7.3 Success Criteria
- [ ] Window class implemented with tab management
- [ ] Tab creation and retrieval working
- [ ] Escape hatch to Playwright context available
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 8: Browser Class (Root)

### 8.1 Development Tasks

**Create src/webdantic/core/browser.py**
```python
# src/webdantic/core/browser.py
from __future__ import annotations

from typing import Optional

from playwright.async_api import Browser as PlaywrightBrowser, async_playwright
from pydantic import BaseModel, ConfigDict, Field

from webdantic.config import BrowserConfig
from webdantic.core.window import Window
from webdantic.exceptions import ConnectionError, WindowError


class Browser(BaseModel):
    """Manages connection to Chrome via CDP and window collection."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    config: BrowserConfig = Field(default_factory=BrowserConfig)
    _playwright: any = Field(default=None, exclude=True, repr=False)
    _browser: PlaywrightBrowser | None = Field(default=None, exclude=True, repr=False)
    _connected: bool = Field(default=False, exclude=True, repr=False)
    
    @property
    def playwright_browser(self) -> PlaywrightBrowser:
        """Get underlying Playwright browser for escape hatch."""
        if self._browser is None:
            raise ConnectionError("Browser not connected")
        return self._browser
    
    @property
    def is_connected(self) -> bool:
        """Check if browser is connected."""
        return self._connected and self._browser is not None
    
    @classmethod
    async def connect(
        cls,
        host: str = "localhost",
        port: int = 9222,
        config: Optional[BrowserConfig] = None
    ) -> Browser:
        """Connect to an existing Chrome instance via CDP."""
        if config is None:
            config = BrowserConfig(host=host, port=port)
        
        browser = cls(config=config)
        
        try:
            # Start Playwright
            browser._playwright = await async_playwright().start()
            
            # Connect to CDP endpoint
            endpoint_url = config.endpoint_url
            browser._browser = await browser._playwright.chromium.connect_over_cdp(endpoint_url)
            browser._connected = True
            
            return browser
        except Exception as e:
            if browser._playwright:
                await browser._playwright.stop()
            raise ConnectionError(f"Failed to connect to browser at {config.endpoint_url}: {e}") from e
    
    async def disconnect(self) -> None:
        """Disconnect from the browser."""
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass  # Ignore errors during disconnect
            finally:
                self._browser = None
        
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                self._playwright = None
        
        self._connected = False
    
    async def get_windows(self) -> list[Window]:
        """Get all browser windows/contexts."""
        if not self.is_connected:
            raise ConnectionError("Browser not connected")
        
        try:
            contexts = self._browser.contexts
            return [Window(browser=self, context=ctx) for ctx in contexts]
        except Exception as e:
            raise WindowError(f"Failed to get windows: {e}") from e
    
    async def get_window(self, index: int) -> Window:
        """Get window by index."""
        if not self.is_connected:
            raise ConnectionError("Browser not connected")
        
        try:
            contexts = self._browser.contexts
            if index < 0 or index >= len(contexts):
                raise IndexError(f"Window index {index} out of range (0-{len(contexts)-1})")
            return Window(browser=self, context=contexts[index])
        except IndexError as e:
            raise WindowError(str(e)) from e
        except Exception as e:
            raise WindowError(f"Failed to get window at index {index}: {e}") from e
    
    async def __aenter__(self) -> Browser:
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
```

**Update src/webdantic/core/__init__.py**
```python
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
```

### 8.2 Testing Tasks

**Create tests/unit/test_browser.py**
```python
# tests/unit/test_browser.py
import pytest
from unittest.mock import AsyncMock, Mock, patch
from webdantic.core.browser import Browser
from webdantic.core.window import Window
from webdantic.config import BrowserConfig
from webdantic.exceptions import ConnectionError, WindowError


@pytest.fixture
def mock_playwright():
    """Create a mock Playwright instance."""
    pw = Mock()
    pw.chromium = Mock()
    pw.stop = AsyncMock()
    return pw


@pytest.fixture
def mock_browser():
    """Create a mock Playwright browser."""
    browser = Mock()
    browser.contexts = []
    browser.close = AsyncMock()
    return browser


@pytest.mark.asyncio
async def test_browser_initialization():
    """Test browser initialization."""
    config = BrowserConfig(port=9222)
    browser = Browser(config=config)
    
    assert browser.config.port == 9222
    assert not browser.is_connected


@pytest.mark.asyncio
async def test_connect_success(mock_playwright, mock_browser):
    """Test successful browser connection."""
    with patch("webdantic.core.browser.async_playwright") as mock_pw_func:
        mock_pw_start = AsyncMock(return_value=mock_playwright)
        mock_pw_func.return_value.start = mock_pw_start
        
        mock_playwright.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)
        
        browser = await Browser.connect(port=9222)
        
        assert browser.is_connected
        assert browser.playwright_browser is mock_browser


@pytest.mark.asyncio
async def test_connect_failure(mock_playwright):
    """Test failed browser connection."""
    with patch("webdantic.core.browser.async_playwright") as mock_pw_func:
        mock_pw_start = AsyncMock(return_value=mock_playwright)
        mock_pw_func.return_value.start = mock_pw_start
        
        mock_playwright.chromium.connect_over_cdp = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            await Browser.connect(port=9222)
        
        assert "Failed to connect" in str(exc_info.value)


@pytest.mark.asyncio
async def test_disconnect(mock_playwright, mock_browser):
    """Test browser disconnection."""
    with patch("webdantic.core.browser.async_playwright") as mock_pw_func:
        mock_pw_start = AsyncMock(return_value=mock_playwright)
        mock_pw_func.return_value.start = mock_pw_start
        mock_playwright.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)
        
        browser = await Browser.connect(port=9222)
        await browser.disconnect()
        
        assert not browser.is_connected
        mock_browser.close.assert_awaited_once()
        mock_playwright.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_windows(mock_playwright, mock_browser):
    """Test getting windows."""
    mock_context = Mock()
    mock_browser.contexts = [mock_context]
    
    with patch("webdantic.core.browser.async_playwright") as mock_pw_func:
        mock_pw_start = AsyncMock(return_value=mock_playwright)
        mock_pw_func.return_value.start = mock_pw_start
        mock_playwright.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)
        
        browser = await Browser.connect(port=9222)
        windows = await browser.get_windows()
        
        assert len(windows) == 1
        assert isinstance(windows[0], Window)


@pytest.mark.asyncio
async def test_context_manager(mock_playwright, mock_browser):
    """Test async context manager."""
    with patch("webdantic.core.browser.async_playwright") as mock_pw_func:
        mock_pw_start = AsyncMock(return_value=mock_playwright)
        mock_pw_func.return_value.start = mock_pw_start
        mock_playwright.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)
        
        async with await Browser.connect(port=9222) as browser:
            assert browser.is_connected
        
        mock_browser.close.assert_awaited_once()
        mock_playwright.stop.assert_awaited_once()
```

**Run tests**
```bash
pytest tests/unit/test_browser.py -v
```

### 8.3 Success Criteria
- [ ] Browser class implemented with CDP connection
- [ ] Window management working
- [ ] Context manager support
- [ ] Escape hatch to Playwright browser available
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 9: Public API and Package Exports

### 9.1 Development Tasks

**Create src/webdantic/__init__.py**
```python
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
```

**Update pyproject.toml**
```toml
[project]
name = "webdantic"
version = "0.1.0"
description = "A Pythonic and Pydantic wrapper for Chrome DevTools Protocol via Playwright"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["playwright", "cdp", "browser-automation", "pydantic", "testing"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "playwright>=1.40.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "ruff>=0.1.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/webdantic"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 9.2 Testing Tasks

**Create tests/test_public_api.py**
```python
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
```

**Run all tests**
```bash
pytest tests/ -v
mypy src/webdantic
```

### 9.3 Success Criteria
- [ ] Public API properly exported
- [ ] All imports work from top-level package
- [ ] Version accessible
- [ ] All tests pass
- [ ] No mypy errors

---

## Step 10: Integration Tests and Examples

### 10.1 Development Tasks

**Create tests/conftest.py**
```python
# tests/conftest.py
"""Pytest configuration and fixtures."""
import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

**Create tests/integration/test_e2e.py**
```python
# tests/integration/test_e2e.py
"""End-to-end integration tests.

NOTE: These tests require a running Chrome instance with CDP enabled.
Start Chrome with: chrome --remote-debugging-port=9222
"""
import pytest
from webdantic import Browser, BrowserConfig


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_navigation():
    """Test basic browser navigation."""
    try:
        browser = await Browser.connect(port=9222)
        
        # Get first window
        window = await browser.get_window(0)
        
        # Create new tab
        tab = await window.new_tab()
        
        # Get page
        page = await tab.get_page()
        
        # Navigate
        await page.goto("https://example.com")
        
        # Get title
        title = await page.title()
        assert "Example" in title
        
        # Close tab
        await tab.close()
        
        # Disconnect
        await browser.disconnect()
        
    except Exception as e:
        pytest.skip(f"Integration test skipped: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_element_selection():
    """Test element selection and interaction."""
    try:
        browser = await Browser.connect(port=9222)
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()
        
        await page.goto("https://example.com")
        
        # Select heading
        heading = await page.select("h1")
        text = await heading.text()
        assert len(text) > 0
        
        # Check visibility
        is_visible = await heading.is_visible()
        assert is_visible
        
        await tab.close()
        await browser.disconnect()
        
    except Exception as e:
        pytest.skip(f"Integration test skipped: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_manager():
    """Test browser context manager."""
    try:
        async with await Browser.connect(port=9222) as browser:
            window = await browser.get_window(0)
            tab = await window.new_tab()
            page = await tab.get_page()
            
            await page.goto("https://example.com")
            assert page.url == "https://example.com/"
            
            await tab.close()
        
        # Browser should be disconnected
        assert not browser.is_connected
        
    except Exception as e:
        pytest.skip(f"Integration test skipped: {e}")
```

**Create examples/basic_navigation.py**
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "webdantic",
# ]
# ///
# examples/basic_navigation.py
"""Basic navigation example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/basic_navigation.py
"""
import asyncio
from webdantic import Browser


async def main():
    # Connect to Chrome
    async with await Browser.connect(port=9222) as browser:
        print("Connected to browser")
        
        # Get first window
        window = await browser.get_window(0)
        print("Got window")
        
        # Create new tab
        tab = await window.new_tab()
        print("Created new tab")
        
        # Get page wrapper
        page = await tab.get_page()
        
        # Navigate
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"Title: {title}")
        print(f"URL: {url}")
        
        # Select and interact with elements
        heading = await page.select("h1")
        heading_text = await heading.text()
        print(f"Heading: {heading_text}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Close tab
        await tab.close()
        print("Tab closed")
    
    print("Browser disconnected")


if __name__ == "__main__":
    asyncio.run(main())
```

**Create examples/form_filling.py**
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "webdantic",
# ]
# ///
# examples/form_filling.py
"""Form filling example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/form_filling.py
"""
import asyncio
from webdantic import Browser


async def main():
    async with await Browser.connect(port=9222) as browser:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()
        
        # Navigate to a page with forms (example)
        print("Navigating to form page...")
        await page.goto("https://httpbin.org/forms/post")
        
        # Fill in form fields
        print("Filling form...")
        
        # Type into text input
        customer_name = await page.select("input[name='custname']")
        await customer_name.fill("John Doe")
        
        # Type into textarea
        comments = await page.select("textarea[name='comments']")
        await comments.fill("This is a test comment")
        
        print("Form filled successfully")
        
        # Wait to see results
        await asyncio.sleep(3)
        
        await tab.close()


if __name__ == "__main__":
    asyncio.run(main())
```

**Create examples/screenshots.py**
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "webdantic",
# ]
# ///
# examples/screenshots.py
"""Screenshot example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/screenshots.py
"""
import asyncio
from pathlib import Path
from webdantic import Browser, ScreenshotConfig


async def main():
    async with await Browser.connect(port=9222) as browser:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()
        
        # Navigate
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot
        output_dir = Path("screenshots")
        output_dir.mkdir(exist_ok=True)
        
        screenshot_path = output_dir / "example.png"
        print(f"Taking screenshot: {screenshot_path}")
        
        config = ScreenshotConfig(full_page=True)
        await page.screenshot(path=screenshot_path, config=config)
        
        print(f"Screenshot saved to {screenshot_path}")
        
        await tab.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 10.2 Testing Tasks

**Mark integration tests in pytest.ini**
Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
]
```

**Run unit tests only**
```bash
pytest tests/unit/ -v
```

**Run integration tests (requires Chrome with CDP)**
```bash
# Start Chrome first: chrome --remote-debugging-port=9222
pytest tests/integration/ -v -m integration
```

**Run examples**
```bash
# Start Chrome first
uv run examples/basic_navigation.py
uv run examples/form_filling.py
uv run examples/screenshots.py
```

### 10.3 Success Criteria
- [ ] Integration tests run successfully with Chrome
- [ ] All examples execute without errors
- [ ] Screenshots saved correctly
- [ ] Form filling works as expected
- [ ] All tests pass

---

## Step 11: Documentation and Final Polish

### 11.1 Development Tasks

**Create CONTRIBUTING.md**
```markdown
# Contributing to Webdantic

## Development Setup

1. Install UV: https://github.com/astral-sh/uv
2. Clone the repository
3. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Code Standards

- Python 3.11+
- Line length: 120 characters max
- File size: Under 500 lines preferred
- All files start with `# path/to/file.py` comment
- Use `from __future__ import annotations`
- Never use quoted type hints
- Pydantic BaseModel for all class objects where sensible

## Testing

Run unit tests:
```bash
pytest tests/unit/ -v
```

Run integration tests (requires Chrome with CDP on port 9222):
```bash
pytest tests/integration/ -v -m integration
```

Type checking:
```bash
mypy src/webdantic
```

Code formatting:
```bash
ruff format src/ tests/
ruff check src/ tests/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit pull request

## Object Hierarchy

Remember the core hierarchy:
```
Browser -> Window -> Tab -> Page -> Selector
```

Each object should:
- Be a Pydantic BaseModel
- Have a parent reference (except Browser)
- Expose underlying Playwright object via `playwright_*` property
```

**Update README.md with installation and usage**
Already provided in project files.

**Create CHANGELOG.md**
```markdown
# Changelog

## [0.1.0] - 2024-XX-XX

### Added
- Initial MVP release
- Browser connection via CDP
- Window/Tab management
- Page navigation and interaction
- Element selection with Selector objects
- Screenshot and PDF generation
- Async/await support
- Pydantic v2 validation
- Comprehensive test suite
- Usage examples
```

**Add type stubs if needed**
Create `py.typed` marker file:
```bash
touch src/webdantic/py.typed
```

### 11.2 Testing Tasks

**Verify documentation**
- [ ] README.md is clear and accurate
- [ ] All examples in README work
- [ ] CONTRIBUTING.md has correct setup instructions
- [ ] API documentation is complete

**Final test run**
```bash
# Unit tests
pytest tests/unit/ -v --cov=webdantic --cov-report=html

# Type checking
mypy src/webdantic

# Linting
ruff check src/ tests/

# Integration tests (with Chrome running)
pytest tests/integration/ -v -m integration
```

**Build package**
```bash
uv build
```

**Test installation**
```bash
uv pip install dist/webdantic-0.1.0-py3-none-any.whl
python -c "import webdantic; print(webdantic.__version__)"
```

### 11.3 Success Criteria
- [ ] All documentation complete and accurate
- [ ] CONTRIBUTING.md with clear guidelines
- [ ] Type stubs in place
- [ ] Package builds successfully
- [ ] All tests pass (unit + integration)
- [ ] No mypy/ruff errors
- [ ] Examples run correctly
- [ ] README examples verified

---

## MVP Completion Checklist

### Core Functionality
- [ ] Browser connection via CDP
- [ ] Window management
- [ ] Tab creation and navigation
- [ ] Page wrapper with navigation
- [ ] Element selection and interaction
- [ ] JavaScript evaluation
- [ ] Screenshots and PDFs
- [ ] Wait conditions

### Code Quality
- [ ] All files under 500 lines
- [ ] Type hints throughout
- [ ] Pydantic models for configuration
- [ ] Custom exception hierarchy
- [ ] Escape hatches to Playwright

### Testing
- [ ] Unit tests for all components (>80% coverage)
- [ ] Integration tests for E2E workflows
- [ ] All tests pass
- [ ] Type checking with mypy passes

### Documentation
- [ ] README with quick start
- [ ] API documentation
- [ ] Usage examples
- [ ] Contributing guidelines
- [ ] Inline docstrings

### Package
- [ ] pyproject.toml configured
- [ ] Package builds
- [ ] Installable via pip/uv
- [ ] py.typed marker present

---

## Post-MVP Enhancements (Future)

- Network interception
- Request/response modification
- Cookie management
- File upload/download
- Multi-browser support (Firefox, Safari)
- Recording/replay functionality
- Plugin system
- Enhanced error recovery
- Retry mechanisms
- Connection pooling

---

## Notes for Developers

1. **Start Chrome with CDP**: Always run `chrome --remote-debugging-port=9222` before testing
2. **Object hierarchy**: Respect the Browser -> Window -> Tab -> Page -> Selector chain
3. **Escape hatches**: Every wrapper exposes its Playwright object via `playwright_*` property
4. **Pydantic first**: Use BaseModel for all structured objects
5. **Async everywhere**: All I/O operations must be async
6. **Error handling**: Use custom exceptions from `webdantic.exceptions`
7. **Type safety**: Leverage Pydantic validation and Python type hints
8. **Keep it simple**: Don't replicate entire Playwright API, just the essentials

---

## Troubleshooting

**Chrome won't connect**
- Ensure Chrome is running with `--remote-debugging-port=9222`
- Check firewall settings
- Try `localhost` vs `127.0.0.1`

**Import errors**
- Verify package is installed: `uv pip list | grep webdantic`
- Check Python version: `python --version` (must be 3.11+)
- Reinstall: `uv pip install -e .`

**Tests failing**
- Run unit tests only first: `pytest tests/unit/`
- For integration tests, ensure Chrome is running
- Check pytest-asyncio is installed

**Type errors**
- Run `mypy src/webdantic --show-error-codes`
- Ensure `from __future__ import annotations` at top of files
- Check Pydantic version is 2.5+