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