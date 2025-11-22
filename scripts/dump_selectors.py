#!/usr/bin/env python3
"""
Dump detailed selector info from a given URL as JSON.

Features:
- Normalizes and validates the input URL (adds https:// if missing).
- Uses Webdantic to connect to a CDP-enabled Chrome instance.
- Walks the DOM in the page via JS and collects detailed element info.
- Serializes into nested Pydantic v2 models.
- Prints JSON to stdout.
- Saves each run to: ./selector_dumps/<timestamp>_<host>/dump.json

Prerequisites:
1. Start Chrome (or Chromium) with CDP enabled, e.g.:
   chrome --remote-debugging-port=9222

2. Run this script, for example:
   uv run examples/dump_selectors.py --url "https://example.com"

"""
from __future__ import annotations
import argparse
import asyncio
import sys
import json

from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, ConfigDict, Field, RootModel

from webdantic import Browser



# Default directory to save dumps
dump_dir = Path(__file__).parent / "selector_dumps"


# ---------------------------------------------------------------------------
# URL normalization
# ---------------------------------------------------------------------------

def normalize_url(raw: str) -> str:
    """
    Normalize and validate a URL.

    - Strips whitespace
    - Adds https:// if no scheme is present
    - Ensures there is a hostname (netloc)
    """
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("URL must not be empty")

    parsed = urlparse(raw)

    # If no scheme, assume https
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = urlparse(raw)

    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {raw!r}")

    return urlunparse(parsed)


# ---------------------------------------------------------------------------
# Pydantic models (nested / structured JSON)
# ---------------------------------------------------------------------------

class BoundingClientRect(BaseModel):
    x: float
    y: float
    top: float
    left: float
    right: float
    bottom: float
    width: float
    height: float


class DataAttributes(BaseModel):
    # Explicit wrapper so JSON shows:
    # "data_attributes": { "values": { "data-foo": "bar", ... } }
    values: dict[str, str] = Field(default_factory=dict)





class ElementNode(BaseModel):
    """
    A DOM element node with selector info and nested children.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: int
    tag: str

    id: str | None = None
    classes: list[str] = Field(default_factory=list)

    name: str | None = None
    type: str | None = None
    role: str | None = None
    aria_label: str | None = None

    text: str | None = None
    simple_selector: str
    dom_path: str

    href: str | None = None
    src: str | None = None

    data_attributes: DataAttributes = Field(default_factory=DataAttributes)
    bounding_client_rect: BoundingClientRect | None = None

    is_clickable: bool = False
    is_visible: bool = True

    children: list[ElementNode] = Field(default_factory=list)


class SelectorDump(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    title: str
    total_elements: int
    elements: list[ElementNode]
    raw_meta: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# JS snippet executed in the page to collect DOM data
# ---------------------------------------------------------------------------

'''JS_COLLECT_SELECTORS = """
(() => {
  function getSimpleSelector(el) {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) {
      return "#" + CSS.escape(el.id);
    }
    let sel = el.tagName.toLowerCase();
    if (el.classList && el.classList.length > 0) {
      sel += "." + Array.from(el.classList).map(c => CSS.escape(c)).join(".");
    }
    return sel;
  }

  function getDomPath(el) {
    if (!el || el.nodeType !== 1) return "";
    const stack = [];
    let node = el;

    while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== "html") {
      let sibCount = 0;
      let sibIndex = 0;
      const tag = node.tagName.toLowerCase();

      let sib = node.parentNode ? node.parentNode.firstElementChild : null;
      while (sib) {
        if (sib.tagName === node.tagName) {
          if (sib === node) {
            sibIndex = sibCount;
          }
          sibCount++;
        }
        sib = sib.nextElementSibling;
      }

      let part = tag;
      if (sibCount > 1) {
        part += `:nth-of-type(${sibIndex + 1})`;
      }
      stack.unshift(part);
      node = node.parentNode;
    }

    return "html > " + stack.join(" > ");
  }

  function getBoundingRect(el) {
    try {
      const rect = el.getBoundingClientRect();
      return {
        x: rect.x,
        y: rect.y,
        top: rect.top,
        left: rect.left,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    } catch (e) {
      return null;
    }
  }

  function isVisible(el) {
    if (!el || el.nodeType !== 1) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function isClickable(el) {
    if (!el || el.nodeType !== 1) return false;
    const tag = el.tagName.toLowerCase();
    if (["a", "button", "summary"].includes(tag)) return true;
    if (tag === "input") {
      const type = (el.getAttribute("type") || "").toLowerCase();
      if (["button", "submit", "reset", "checkbox", "radio", "image"].includes(type)) {
        return true;
      }
    }
    const role = (el.getAttribute("role") || "").toLowerCase();
    if (["button", "link", "tab", "menuitem"].includes(role)) return true;

    const onclick = el.getAttribute("onclick");
    if (onclick && onclick.trim().length > 0) return true;

    return false;
  }

  function dataAttributes(el) {
    const result = {};
    for (const attr of el.attributes || []) {
      if (attr.name && attr.name.startsWith("data-")) {
        result[attr.name] = attr.value;
      }
    }
    return result;
  }

  const elements = Array.from(document.querySelectorAll("*"));
  return elements.map((el, index) => {
    const rect = getBoundingRect(el);
    const text = (el.innerText || "")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, 200);

    return {
      index,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: Array.from(el.classList || []),

      name: el.getAttribute("name"),
      type: el.getAttribute("type"),
      role: el.getAttribute("role"),
      aria_label: el.getAttribute("aria-label"),

      text: text || null,
      simple_selector: getSimpleSelector(el),
      dom_path: getDomPath(el),

      href: el.getAttribute("href"),
      src: el.getAttribute("src"),

      // This matches DataAttributes(RootModel[dict[str, str]])
      data_attributes: dataAttributes(el),

      bounding_client_rect: rect,
      is_clickable: isClickable(el),
      is_visible: isVisible(el),
    };
  });
})();
"""'''

# ---------------------------------------------------------------------------
# JS snippet executed in the page to collect DOM data
# ---------------------------------------------------------------------------

JS_COLLECT_SELECTORS = """
(() => {
  function getSimpleSelector(el) {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) {
      return "#" + CSS.escape(el.id);
    }
    let sel = el.tagName.toLowerCase();
    if (el.classList && el.classList.length > 0) {
      sel += "." + Array.from(el.classList).map(c => CSS.escape(c)).join(".");
    }
    return sel;
  }

  function getDomPath(el) {
    if (!el || el.nodeType !== 1) return "";
    const stack = [];
    let node = el;

    while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== "html") {
      let sibCount = 0;
      let sibIndex = 0;
      const tag = node.tagName.toLowerCase();

      let sib = node.parentNode ? node.parentNode.firstElementChild : null;
      while (sib) {
        if (sib.tagName === node.tagName) {
          if (sib === node) {
            sibIndex = sibCount;
          }
          sibCount++;
        }
        sib = sib.nextElementSibling;
      }

      let part = tag;
      if (sibCount > 1) {
        part += `:nth-of-type(${sibIndex + 1})`;
      }
      stack.unshift(part);
      node = node.parentNode;
    }

    return "html > " + stack.join(" > ");
  }

  function getBoundingRect(el) {
    try {
      const rect = el.getBoundingClientRect();
      return {
        x: rect.x,
        y: rect.y,
        top: rect.top,
        left: rect.left,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    } catch (e) {
      return null;
    }
  }

  function isVisible(el) {
    if (!el || el.nodeType !== 1) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function isClickable(el) {
    if (!el || el.nodeType !== 1) return false;
    const tag = el.tagName.toLowerCase();
    if (["a", "button", "summary"].includes(tag)) return true;
    if (tag === "input") {
      const type = (el.getAttribute("type") || "").toLowerCase();
      if (["button", "submit", "reset", "checkbox", "radio", "image"].includes(type)) {
        return true;
      }
    }
    const role = (el.getAttribute("role") || "").toLowerCase();
    if (["button", "link", "tab", "menuitem"].includes(role)) return true;

    const onclick = el.getAttribute("onclick");
    if (onclick && onclick.trim().length > 0) return true;

    return false;
  }

  function dataAttributes(el) {
    const result = {};
    for (const attr of el.attributes || []) {
      if (attr.name && attr.name.startsWith("data-")) {
        result[attr.name] = attr.value;
      }
    }
    return result;
  }

  const elements = Array.from(document.querySelectorAll("*"));
  return elements.map((el, index) => {
    const rect = getBoundingRect(el);
    const text = (el.innerText || "")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, 200);

    return {
      index,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: Array.from(el.classList || []),

      name: el.getAttribute("name"),
      type: el.getAttribute("type"),
      role: el.getAttribute("role"),
      aria_label: el.getAttribute("aria-label"),

      text: text || null,
      simple_selector: getSimpleSelector(el),
      dom_path: getDomPath(el),

      href: el.getAttribute("href"),
      src: el.getAttribute("src"),

      // matches DataAttributes(values=...)
      data_attributes: {
        values: dataAttributes(el)
      },

      bounding_client_rect: rect,
      is_clickable: isClickable(el),
      is_visible: isVisible(el),
    };
  });
})();
"""

JS_COLLECT_SELECTOR_TREE = """
(() => {
  function getSimpleSelector(el) {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) {
      return "#" + CSS.escape(el.id);
    }
    let sel = el.tagName.toLowerCase();
    if (el.classList && el.classList.length > 0) {
      sel += "." + Array.from(el.classList).map(c => CSS.escape(c)).join(".");
    }
    return sel;
  }

  function getDomPath(el) {
    if (!el || el.nodeType !== 1) return "";
    const stack = [];
    let node = el;

    while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== "html") {
      let sibCount = 0;
      let sibIndex = 0;
      const tag = node.tagName.toLowerCase();

      let sib = node.parentNode ? node.parentNode.firstElementChild : null;
      while (sib) {
        if (sib.tagName === node.tagName) {
          if (sib === node) {
            sibIndex = sibCount;
          }
          sibCount++;
        }
        sib = sib.nextElementSibling;
      }

      let part = tag;
      if (sibCount > 1) {
        part += `:nth-of-type(${sibIndex + 1})`;
      }
      stack.unshift(part);
      node = node.parentNode;
    }

    return "html > " + stack.join(" > ");
  }

  function getBoundingRect(el) {
    try {
      const rect = el.getBoundingClientRect();
      return {
        x: rect.x,
        y: rect.y,
        top: rect.top,
        left: rect.left,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    } catch (e) {
      return null;
    }
  }

  function isVisible(el) {
    if (!el || el.nodeType !== 1) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function isClickable(el) {
    if (!el || el.nodeType !== 1) return false;
    const tag = el.tagName.toLowerCase();
    if (["a", "button", "summary"].includes(tag)) return true;
    if (tag === "input") {
      const type = (el.getAttribute("type") || "").toLowerCase();
      if (["button", "submit", "reset", "checkbox", "radio", "image"].includes(type)) {
        return true;
      }
    }
    const role = (el.getAttribute("role") || "").toLowerCase();
    if (["button", "link", "tab", "menuitem"].includes(role)) return true;

    const onclick = el.getAttribute("onclick");
    if (onclick && onclick.trim().length > 0) return true;

    return false;
  }

  function dataAttributes(el) {
    const result = {};
    for (const attr of el.attributes || []) {
      if (attr.name && attr.name.startsWith("data-")) {
        result[attr.name] = attr.value;
      }
    }
    return result;
  }

  let globalIndex = 0;

  function walk(el) {
    if (!el || el.nodeType !== 1) return null;

    const index = globalIndex++;
    const rect = getBoundingRect(el);
    const text = (el.innerText || "")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, 200);

    const node = {
      index,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: Array.from(el.classList || []),

      name: el.getAttribute("name"),
      type: el.getAttribute("type"),
      role: el.getAttribute("role"),
      aria_label: el.getAttribute("aria-label"),

      text: text || null,
      simple_selector: getSimpleSelector(el),
      dom_path: getDomPath(el),

      href: el.getAttribute("href"),
      src: el.getAttribute("src"),

      data_attributes: {
        values: dataAttributes(el)
      },

      bounding_client_rect: rect,
      is_clickable: isClickable(el),
      is_visible: isVisible(el),

      children: [],
    };

    const children = Array.from(el.children || []);
    for (const childEl of children) {
      const childNode = walk(childEl);
      if (childNode) {
        node.children.push(childNode);
      }
    }

    return node;
  }

  const rootEl = document.documentElement; // <html>
  return walk(rootEl);
})();
"""

# ---------------------------------------------------------------------------
# Core logic: connect with Webdantic and collect dump
# ---------------------------------------------------------------------------

'''async def dump_selectors(url: str, host: str, port: int) -> SelectorDump:
    """Connect to Chrome via Webdantic, load URL, and dump selector info."""
    browser = await Browser.connect(host=host, port=port)

    try:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        title = await page.title()
        elements_raw = await page.evaluate(JS_COLLECT_SELECTORS)

        elements = [ElementNode(**el) for el in elements_raw]

        dump = SelectorDump(
            url=url,
            title=title,
            total_elements=len(elements),
            elements=elements,
            raw_meta={"window_index": 0},
        )

        await tab.close()
        return dump
    finally:
        await browser.disconnect()'''

async def dump_selectors(url: str, host: str, port: int) -> SelectorDump:
    """Connect to Chrome via Webdantic, load URL, and dump a DOM-shaped selector tree."""
    browser = await Browser.connect(host=host, port=port)

    try:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        title = await page.title()
        root_raw = await page.evaluate(JS_COLLECT_SELECTOR_TREE)

        root = ElementNode(**root_raw)

        def count_nodes(node: ElementNode) -> int:
            return 1 + sum(count_nodes(child) for child in node.children)

        total = count_nodes(root)

        dump = SelectorDump(
            url=url,
            title=title,
            total_elements=total,
            root=root,
            raw_meta={"window_index": 0},
        )

        await tab.close()
        return dump
    finally:
        await browser.disconnect()

# ---------------------------------------------------------------------------
# Saving to disk
# ---------------------------------------------------------------------------
'''
def save_selector_dump(
    dump: SelectorDump,
    dump_dir: Path | None = None,
) -> Path:
    """
    Save a SelectorDump as a JSON file in:

        dump_dir = Path(__file__).parent / "selector_dumps"
        subfolder = "<YYYYMMDD_HHMMSS>_<host>/dump.json"

    Returns the path to the created file.
    """
    if dump_dir is None:
        dump_dir = Path(__file__).parent / "selector_dumps"

    parsed = urlparse(dump.url)
    host = parsed.netloc or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    subdir_name = f"{timestamp}_{host}"
    run_dir = dump_dir / subdir_name
    run_dir.mkdir(parents=True, exist_ok=True)

    file_path = run_dir / "dump.json"
    file_path.write_text(dump.model_dump_json(indent=2), encoding="utf-8")
    return file_path
'''


def save_selector_dump(
    dump: SelectorDump,
    dump_dir: Path | None = None,
) -> Path:
    """
    Save a SelectorDump as a JSON file in:

        dump_dir = Path(__file__).parent / "selector_dumps"
        subfolder = "<YYYYMMDD_HHMMSS>_<host>/dump.json"

    Returns the path to the created file.
    """
    if dump_dir is None:
        dump_dir = Path(__file__).parent / "selector_dumps"

    normalized_urldir = dump.url.replace("://", "_").replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_").replace(".", "_")
    parsed = urlparse(dump.url)
    host = parsed.netloc or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    subdir_name = f"{host}".replace(":", "_").replace("/", "_").replace(".", "_")
    run_dir = dump_dir / subdir_name
    run_dir.mkdir(parents=True, exist_ok=True)

    file_path = run_dir  / f"{timestamp}" / f"{normalized_urldir}.json"
    if len(file_path.name) > 255:
        prelim_name = run_dir  / f"{timestamp}" 
        prelim_len = len(str(prelim_name))
        extra_len = 250-prelim_len
        file_path = run_dir / f"{timestamp}" / f"{normalized_urldir[:extra_len]}.json"
        
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(dump.model_dump_json(indent=2), encoding="utf-8")
    return file_path

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dump detailed selector information for a URL via Webdantic."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to analyze (e.g. https://example.com or example.com)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="CDP host for Chrome (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="CDP port for Chrome (default: 9222)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for stdout (default: 2)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        normalized_url = normalize_url(args.url)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    async def _run() -> None:
        dump = await dump_selectors(
            url=normalized_url,
            host=args.host,
            port=args.port,
        )
        # Print to stdout
        print(dump.model_dump_json(indent=args.indent))

        # Also save to disk
        saved_path = save_selector_dump(dump)
        print(f"\nSaved dump to: {saved_path}", file=sys.stderr)

    asyncio.run(_run())


if __name__ == "__main__":
    main()




'''

def normalize_url(raw: str) -> str:
    """
    Normalize and validate a URL.

    - Strips whitespace
    - Adds https:// if no scheme is present
    - Ensures there is a hostname (netloc)
    """
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("URL must not be empty")

    parsed = urlparse(raw)

    # If no scheme, assume https
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = urlparse(raw)

    if not parsed.netloc:
        # Still no host part -> invalid URL
        raise ValueError(f"Invalid URL: {raw!r}")

    # You can do additional checks here if desired
    return urlunparse(parsed)


class ElementSelectorDetail(BaseModel):
    """Detailed info about a single DOM element and its selectors."""

    index: int
    tag: str

    id: str | None = None
    classes: list[str] = Field(default_factory=list)

    name: str | None = None
    type: str | None = None
    role: str | None = None
    aria_label: str | None = None

    text: str | None = None  # trimmed innerText snippet
    simple_selector: str
    dom_path: str  # (rough) unique-ish CSS path

    href: str | None = None
    src: str | None = None

    data_attributes: dict[str, str] = Field(default_factory=dict)

    # Layout-ish info (viewport coordinates, not full layout engine)
    bounding_client_rect: dict[str, float] | None = None

    # Heuristics about "clickability"
    is_clickable: bool = False
    is_visible: bool = True


class SelectorDump(BaseModel):
    """Top-level dump with page + element metadata."""

    url: str
    title: str
    total_elements: int
    elements: list[ElementSelectorDetail]

    raw_meta: dict[str, Any] = Field(default_factory=dict)


# JavaScript executed in the page context to collect data.
JS_COLLECT_SELECTORS = """
(() => {
  function getSimpleSelector(el) {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) {
      return "#" + CSS.escape(el.id);
    }
    let sel = el.tagName.toLowerCase();
    if (el.classList && el.classList.length > 0) {
      sel += "." + Array.from(el.classList).map(c => CSS.escape(c)).join(".");
    }
    return sel;
  }

  function getDomPath(el) {
    if (!el || el.nodeType !== 1) return "";
    const stack = [];
    let node = el;

    while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== "html") {
      let sibCount = 0;
      let sibIndex = 0;
      const tag = node.tagName.toLowerCase();

      let sib = node.parentNode ? node.parentNode.firstElementChild : null;
      while (sib) {
        if (sib.tagName === node.tagName) {
          if (sib === node) {
            sibIndex = sibCount;
          }
          sibCount++;
        }
        sib = sib.nextElementSibling;
      }

      let part = tag;
      if (sibCount > 1) {
        part += `:nth-of-type(${sibIndex + 1})`;
      }
      stack.unshift(part);
      node = node.parentNode;
    }

    return "html > " + stack.join(" > ");
  }

  function getBoundingRect(el) {
    try {
      const rect = el.getBoundingClientRect();
      return {
        x: rect.x,
        y: rect.y,
        top: rect.top,
        left: rect.left,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    } catch (e) {
      return null;
    }
  }

  function isVisible(el) {
    if (!el || el.nodeType !== 1) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function isClickable(el) {
    if (!el || el.nodeType !== 1) return false;
    const tag = el.tagName.toLowerCase();
    if (["a", "button", "summary"].includes(tag)) return true;
    if (tag === "input") {
      const type = (el.getAttribute("type") || "").toLowerCase();
      if (["button", "submit", "reset", "checkbox", "radio", "image"].includes(type)) {
        return true;
      }
    }
    const role = (el.getAttribute("role") || "").toLowerCase();
    if (["button", "link", "tab", "menuitem"].includes(role)) return true;

    const onclick = el.getAttribute("onclick");
    if (onclick && onclick.trim().length > 0) return true;

    return false;
  }

  function dataAttributes(el) {
    const result = {};
    for (const attr of el.attributes || []) {
      if (attr.name && attr.name.startsWith("data-")) {
        result[attr.name] = attr.value;
      }
    }
    return result;
  }

  const elements = Array.from(document.querySelectorAll("*"));
  return elements.map((el, index) => {
    const rect = getBoundingRect(el);
    const text = (el.innerText || "")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, 200);

    return {
      index,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: Array.from(el.classList || []),

      name: el.getAttribute("name"),
      type: el.getAttribute("type"),
      role: el.getAttribute("role"),
      aria_label: el.getAttribute("aria-label"),

      text: text || null,
      simple_selector: getSimpleSelector(el),
      dom_path: getDomPath(el),

      href: el.getAttribute("href"),
      src: el.getAttribute("src"),

      data_attributes: dataAttributes(el),

      bounding_client_rect: rect,
      is_clickable: isClickable(el),
      is_visible: isVisible(el),
    };
  });
})();
"""


async def dump_selectors(url: str, host: str, port: int) -> SelectorDump:
    """Connect to Chrome via Webdantic, load URL, and dump selector info."""
    browser = await Browser.connect(host=host, port=port)

    try:
        # Use the first window/context
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        title = await page.title()
        elements_raw = await page.evaluate(JS_COLLECT_SELECTORS)

        # Pydantic-validate each element
        elements: list[ElementSelectorDetail] = [
            ElementSelectorDetail(**el) for el in elements_raw
        ]

        dump = SelectorDump(
            url=url,
            title=title,
            total_elements=len(elements),
            elements=elements,
            raw_meta={"window_index": 0},
        )

        await tab.close()
        return dump
    finally:
        await browser.disconnect()



def save_selector_dump(
    dump: SelectorDump,
    dump_dir: Path | None = None,
) -> Path:
    """
    Save a SelectorDump as a JSON file in:

        dump_dir = Path(__file__).parent / "selector_dumps"
        subfolder = "<YYYYMMDD_HHMMSS>_<host>/dump.json"

    Returns the path to the created file.
    """
    if dump_dir is None:
        dump_dir = Path(__file__).parent / "selector_dumps"

    normalized_urldir = dump.url.replace("://", "_").replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_").replace(".", "_")
    parsed = urlparse(dump.url)
    host = parsed.netloc or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    subdir_name = f"{host}"
    run_dir = dump_dir / subdir_name
    run_dir.mkdir(parents=True, exist_ok=True)

    file_path = run_dir  / f"{timestamp}" / f"{normalized_urldir}.json"
    if len(file_path.name) > 255:
        prelim_name = run_dir  / f"{timestamp}" 
        prelim_len = len(str(prelim_name))
        extra_len = 250-prelim_len
        file_path = run_dir / f"{timestamp}" / f"{normalized_urldir[:extra_len]}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(dump.model_dump_json(indent=2), encoding="utf-8")
    return file_path



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dump detailed selector information for a URL via Webdantic."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to analyze (e.g. https://example.com)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="CDP host for Chrome (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="CDP port for Chrome (default: 9222)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        normalized_url = normalize_url(args.url)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    #timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    #site_dir = dump_dir / 



    async def _run() -> None:
        dump = await dump_selectors(url=normalized_url, host=args.host, port=args.port)
        # model_dump_json is pydantic v2 API
        print(dump.model_dump_json(indent=args.indent))

        # Also save to disk
        saved_path = save_selector_dump(dump)
        print(f"\nSaved dump to: {saved_path}", file=sys.stderr)

    asyncio.run(_run())


if __name__ == "__main__":
    main()

'''