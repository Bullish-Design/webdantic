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