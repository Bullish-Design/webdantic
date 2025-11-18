# src/webdantic/core/page.py
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from playwright.async_api import Page as PlaywrightPage
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.config import ScreenshotConfig
from webdantic.core.selector import Selector
from webdantic.exceptions import NavigationError, SelectorError, TimeoutError
from webdantic.types import CSSSelector, JavaScriptCode, LoadState, WaitUntil

if TYPE_CHECKING:
    from webdantic.core.tab import Tab


class Page(BaseModel):
    """Wrapper for Playwright Page with Pydantic validation."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _tab: Tab = PrivateAttr() #Field(exclude=True, repr=False)
    _playwright_page: PlaywrightPage = PrivateAttr() #Field(exclude=True, repr=False)
    
    def __init__(self, tab: Tab, playwright_page: PlaywrightPage):
        """Initialize Page with tab and Playwright page references."""
        super().__init__() #_tab=tab, _playwright_page=playwright_page)
        self._tab = tab
        self._playwright_page = playwright_page

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
