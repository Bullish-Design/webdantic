# src/webdantic/core/selector.py
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from playwright.async_api import Locator
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.exceptions import SelectorError, TimeoutError
from webdantic.types import CSSSelector

if TYPE_CHECKING:
    from webdantic.core.page import Page


class Selector(BaseModel):
    """Represents a selected element or elements on a page."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Public, serializable field
    selector: CSSSelector = Field(description="CSS selector string")

    # Runtime-only references (not validated or serialized)
    _page: Page = PrivateAttr()
    _locator: Locator = PrivateAttr()
    
    def __init__(self, selector: CSSSelector, page: Page, locator: Locator) -> None:
        """Initialize selector with page and locator references."""
        # Let Pydantic handle only declared fields
        super().__init__(selector=selector)
        # Set private runtime attributes directly
        self._page = page
        self._locator = locator
    
    @property
    def page(self) -> Page:
        """Get parent Page object."""
        return self._page
    
    @property
    def playwright_locator(self) -> Locator:
        """Get underlying Playwright locator for escape hatch."""
        return self._locator
    
    async def click(self, timeout: Optional[int] = None) -> None:
        """Click the element."""
        try:
            await self._locator.click(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to click element '{self.selector}': {e}") from e
    
    async def type(self, text: str, delay: Optional[int] = None, timeout: Optional[int] = None) -> None:
        """Type text into the element character by character."""
        try:
            await self._locator.type(text, delay=delay, timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to type into element '{self.selector}': {e}") from e
    
    async def fill(self, text: str, timeout: Optional[int] = None) -> None:
        """Fill the element with text (clears first)."""
        try:
            await self._locator.fill(text, timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to fill element '{self.selector}': {e}") from e
    
    async def text(self, timeout: Optional[int] = None) -> str:
        """Get text content of the element."""
        try:
            content = await self._locator.text_content(timeout=timeout)
            return content or ""
        except Exception as e:
            raise SelectorError(f"Failed to get text from element '{self.selector}': {e}") from e
    
    async def inner_text(self, timeout: Optional[int] = None) -> str:
        """Get inner text of the element."""
        try:
            return await self._locator.inner_text(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to get inner text from element '{self.selector}': {e}") from e
    
    async def inner_html(self, timeout: Optional[int] = None) -> str:
        """Get inner HTML of the element."""
        try:
            return await self._locator.inner_html(timeout=timeout)
        except Exception as e:
            raise SelectorError(f"Failed to get inner HTML from element '{self.selector}': {e}") from e
    
    async def attribute(self, name: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get attribute value from the element."""
        try:
            return await self._locator.get_attribute(name, timeout=timeout)
        except Exception as e:
            raise SelectorError(
                f"Failed to get attribute '{name}' from element '{self.selector}': {e}"
            ) from e
    
    async def is_visible(self, timeout: Optional[int] = None) -> bool:
        """Check if element is visible."""
        try:
            return await self._locator.is_visible(timeout=timeout)
        except Exception as e:
            raise SelectorError(
                f"Failed to check visibility of element '{self.selector}': {e}"
            ) from e
    
    async def is_hidden(self, timeout: Optional[int] = None) -> bool:
        """Check if element is hidden."""
        try:
            return await self._locator.is_hidden(timeout=timeout)
        except Exception as e:
            raise SelectorError(
                f"Failed to check hidden state of element '{self.selector}': {e}"
            ) from e
    
    async def is_enabled(self, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled."""
        try:
            return await self._locator.is_enabled(timeout=timeout)
        except Exception as e:
            raise SelectorError(
                f"Failed to check enabled state of element '{self.selector}': {e}"
            ) from e
    
    async def is_disabled(self, timeout: Optional[int] = None) -> bool:
        """Check if element is disabled."""
        try:
            return await self._locator.is_disabled(timeout=timeout)
        except Exception as e:
            raise SelectorError(
                f"Failed to check disabled state of element '{self.selector}': {e}"
            ) from e
    
    async def count(self) -> int:
        """Get count of elements matching this selector."""
        try:
            return await self._locator.count()
        except Exception as e:
            raise SelectorError(
                f"Failed to count elements for selector '{self.selector}': {e}"
            ) from e
    
    async def wait_for(
        self,
        state: str = "visible",
        timeout: Optional[int] = None,
    ) -> None:
        """Wait for element to reach a specific state."""
        try:
            await self._locator.wait_for(state=state, timeout=timeout)
        except Exception as e:
            raise TimeoutError(
                f"Timeout waiting for element '{self.selector}' to be {state}: {e}"
            ) from e
