# src/webdantic/core/tab.py
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.async_api import Page as PlaywrightPage
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.core.page import Page
from webdantic.exceptions import NavigationError, TabError

if TYPE_CHECKING:
    from webdantic.core.window import Window


class Tab(BaseModel):
    """Represents an individual tab within a browser window."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _window: Window = PrivateAttr()
    _playwright_page: PlaywrightPage = PrivateAttr()
    _page_wrapper: Page | None = PrivateAttr()

    def __init__(self, window: Window, playwright_page: PlaywrightPage):
        """Initialize Tab with window and Playwright page references."""
        super().__init__() #_window=window, _playwright_page=playwright_page)
        self._window = window
        self._playwright_page = playwright_page
        self._page_wrapper = Page(tab=self, playwright_page=playwright_page)
        
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
