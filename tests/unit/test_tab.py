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