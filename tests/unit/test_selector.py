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