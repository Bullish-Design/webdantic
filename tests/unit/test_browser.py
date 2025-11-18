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