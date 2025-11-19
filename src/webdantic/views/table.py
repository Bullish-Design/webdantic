# src/webdantic/views/table.py
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from webdantic.core.page import Page
from webdantic.core.selector import Selector
from webdantic.exceptions import SelectorError
from webdantic.types import CSSSelector


class TableRow(BaseModel):
    """Single table row (<tr>) backed by a Selector."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: int = Field(..., description="0-based row index (excluding header)")

    _selector: Selector = PrivateAttr()
    _cell_selector: CSSSelector = PrivateAttr()

    def __init__(
        self,
        index: int,
        selector: Selector,
        cell_selector: CSSSelector = "th, td",
    ) -> None:
        super().__init__(index=index)
        self._selector = selector
        self._cell_selector = cell_selector

    @property
    def selector(self) -> Selector:
        """Underlying Selector for this row."""
        return self._selector

    @property
    def page(self) -> Page:
        """Page that owns this row."""
        return self._selector.page

    async def cells(self) -> list[Selector]:
        """
        Return all cell elements (<th>, <td>) for this row as Selector objects.
        """
        try:
            base_locator = self._selector.playwright_locator.locator(
                self._cell_selector
            )
            count = await base_locator.count()

            cells: list[Selector] = []
            for i in range(count):
                nth_locator = base_locator.nth(i)

                cell_css = (
                    f"{self._selector.selector} {self._cell_selector}:nth-match({i + 1})"
                )

                cell_selector = Selector(
                    selector=cell_css,
                    page=self.page,
                    locator=nth_locator,
                )
                cells.append(cell_selector)

            return cells
        except Exception as e:
            raise SelectorError(
                f"Failed to get cells for row '{self._selector.selector}': {e}"
            ) from e

    async def text_cells(self) -> list[str]:
        """
        Convenience helper: get text for each cell in this row.
        """
        cells = await self.cells()
        return [await cell.text() for cell in cells]


class TableView(BaseModel):
    """
    High-level representation of a <table> element.

    Wraps a root table Selector plus row/cell selectors, and yields TableRow
    objects that can in turn yield cell Selectors or texts.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    selector: CSSSelector = Field(..., description="Selector for the table root")
    row_selector: CSSSelector = Field(
        default="tbody tr",
        description="Selector for data rows, relative to the table root",
    )

    _page: Page = PrivateAttr()
    _root: Selector = PrivateAttr()
    _rows: List[TableRow] = PrivateAttr(default_factory=list)
    _cell_selector: CSSSelector = PrivateAttr(default="th, td")

    def __init__(
        self,
        root: Selector,
        row_selector: CSSSelector = "tbody tr",
        cell_selector: CSSSelector = "th, td",
    ) -> None:
        super().__init__(selector=root.selector, row_selector=row_selector)
        self._page = root.page
        self._root = root
        self._cell_selector = cell_selector

    @property
    def page(self) -> Page:
        """Page that owns this table."""
        return self._page

    @property
    def root(self) -> Selector:
        """Root table Selector."""
        return self._root

    @property
    def rows(self) -> list[TableRow]:
        """All table rows discovered for this view."""
        return self._rows

    def __iter__(self):
        return iter(self._rows)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._rows)

    def __getitem__(self, index: int) -> TableRow:  # pragma: no cover - trivial
        return self._rows[index]

    async def load(self) -> None:
        """
        Discover data rows and build TableRow wrappers.

        Uses the underlying Playwright locator of the root selector so that
        row selection is scoped to this table.
        """
        try:
            base_locator = self._root.playwright_locator.locator(self.row_selector)
            count = await base_locator.count()

            rows: list[TableRow] = []
            for i in range(count):
                nth_locator = base_locator.nth(i)

                row_css = (
                    f"{self.selector} {self.row_selector}:nth-match({i + 1})"
                )

                row_selector = Selector(
                    selector=row_css,
                    page=self._page,
                    locator=nth_locator,
                )
                rows.append(
                    TableRow(
                        index=i,
                        selector=row_selector,
                        cell_selector=self._cell_selector,
                    )
                )

            self._rows = rows
        except Exception as e:
            raise SelectorError(
                f"Failed to build TableView for '{self.selector}' "
                f"with rows '{self.row_selector}': {e}"
            ) from e

    @classmethod
    async def from_page(
        cls,
        page: Page,
        table_selector: CSSSelector,
        row_selector: CSSSelector = "tbody tr",
        cell_selector: CSSSelector = "th, td",
    ) -> TableView:
        """
        Convenience constructor: select the table on the given page,
        then load all rows.
        """
        root = await page.select(table_selector)
        view = cls(
            root=root,
            row_selector=row_selector,
            cell_selector=cell_selector,
        )
        await view.load()
        return view

    @classmethod
    async def from_selector(
        cls,
        root: Selector,
        row_selector: CSSSelector = "tbody tr",
        cell_selector: CSSSelector = "th, td",
    ) -> TableView:
        """
        Convenience constructor from an existing table Selector.
        """
        view = cls(
            root=root,
            row_selector=row_selector,
            cell_selector=cell_selector,
        )
        await view.load()
        return view

