# src/webdantic/core/window.py
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.async_api import BrowserContext
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.core.tab import Tab
from webdantic.exceptions import TabError, WindowError

if TYPE_CHECKING:
    from webdantic.core.browser import Browser


class Window(BaseModel):
    """Represents a browser window/context containing tabs."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _browser: Browser = PrivateAttr()
    _context: BrowserContext = PrivateAttr()

    def __init__(self, browser: Browser, context: BrowserContext):
        """Initialize Window with browser and context references."""
        super().__init__()
        self._browser = browser
        self._context = context

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