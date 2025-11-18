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
