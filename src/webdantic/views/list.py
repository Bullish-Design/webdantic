# src/webdantic/views/list.py
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.exceptions import SelectorError
from webdantic.types import CSSSelector


class ListItem(BaseModel):
    """Single item in a list, backed by a Selector."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: int = Field(..., description="0-based position in the list")

    _selector: Selector = PrivateAttr()

    def __init__(self, index: int, selector: Selector) -> None:
        super().__init__(index=index)
        self._selector = selector

    @property
    def selector(self) -> Selector:
        """Underlying Selector for this item."""
        return self._selector

    @property
    def page(self) -> Page:
        """Page that owns this item."""
        return self._selector.page

    async def text(self, timeout: int | None = None) -> str:
        """Get the visible text of the list item."""
        return await self._selector.text(timeout=timeout)

    async def inner_text(self, timeout: int | None = None) -> str:
        """Get the inner text of the list item."""
        return await self._selector.inner_text(timeout=timeout)

    async def click(self, timeout: int | None = None) -> None:
        """Click the list item."""
        await self._selector.click(timeout=timeout)


class ListView(BaseModel):
    """
    High-level representation of a DOM list (e.g. <ul>, <ol>, or a div list).

    This is a thin wrapper on top of a container Selector plus an item selector.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    selector: CSSSelector = Field(..., description="Selector for the list container")
    item_selector: CSSSelector = Field(
        ..., description="Selector for items inside the list container"
    )

    _page: Page = PrivateAttr()
    _root: Selector = PrivateAttr()
    _items: List[ListItem] = PrivateAttr(default_factory=list)

    def __init__(self, root: Selector, item_selector: CSSSelector) -> None:
        super().__init__(selector=root.selector, item_selector=item_selector)
        self._page = root.page
        self._root = root

    @property
    def page(self) -> Page:
        """Page that owns this list."""
        return self._page

    @property
    def root(self) -> Selector:
        """Root container element of the list."""
        return self._root

    @property
    def items(self) -> list[ListItem]:
        """All list items discovered for this view."""
        return self._items

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._items)

    def __getitem__(self, index: int) -> ListItem:  # pragma: no cover - trivial
        return self._items[index]

    async def load(self) -> None:
        """
        Discover items under the container and build ListItem wrappers.

        Uses the underlying Playwright locator of the root selector so that
        item selection is scoped to this container.
        """
        try:
            base_locator = self._root.playwright_locator.locator(self.item_selector)
            count = await base_locator.count()

            items: list[ListItem] = []
            for i in range(count):
                nth_locator = base_locator.nth(i)

                # Descriptive CSS string for debugging / logging only.
                item_css = (
                    f"{self.selector} {self.item_selector}:nth-match({i + 1})"
                )

                item_selector = Selector(
                    selector=item_css,
                    page=self._page,
                    locator=nth_locator,
                )
                items.append(ListItem(index=i, selector=item_selector))

            self._items = items
        except Exception as e:
            raise SelectorError(
                f"Failed to build ListView for '{self.selector}' "
                f"with items '{self.item_selector}': {e}"
            ) from e

    @classmethod
    async def from_page(
        cls,
        page: Page,
        container_selector: CSSSelector,
        item_selector: CSSSelector,
    ) -> ListView:
        """
        Convenience constructor: select the container on the given page,
        then load all items.
        """
        root = await page.select(container_selector)
        view = cls(root=root, item_selector=item_selector)
        await view.load()
        return view

    @classmethod
    async def from_selector(
        cls,
        root: Selector,
        item_selector: CSSSelector,
    ) -> ListView:
        """
        Convenience constructor from an existing container Selector.
        """
        view = cls(root=root, item_selector=item_selector)
        await view.load()
        return view

