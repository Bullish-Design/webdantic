# src/webdantic/core/browser.py
from __future__ import annotations

from typing import Optional, Any

from playwright.async_api import Browser as PlaywrightBrowser, async_playwright
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.config import BrowserConfig
from webdantic.core.window import Window
from webdantic.exceptions import ConnectionError, WindowError


class Browser(BaseModel):
    """Manages connection to Chrome via CDP and window collection."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    config: BrowserConfig = Field(default_factory=BrowserConfig)
    _playwright: Any = PrivateAttr()
    _browser: PlaywrightBrowser | None = PrivateAttr()
    _connected: bool = PrivateAttr()

    def __init__(self, config: BrowserConfig):
        """Initialize Browser with configuration."""
        super().__init__(config=config)
        self._playwright = None
        self._browser = None
        self._connected = False
        
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