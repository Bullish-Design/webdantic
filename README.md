# README.md

# Webdantic

A Pythonic and Pydantic wrapper for Chrome DevTools Protocol (CDP) via Playwright, providing type-safe browser automation with an object-oriented design.

## Philosophy

Webdantic follows "true Smalltalk OOP" principles where Browser, Window, Tab, Page, and Selector are first-class objects with clear hierarchical relationships. Built on Pydantic v2+, it provides type safety and validation while maintaining escape hatches to raw Playwright functionality.

**Core Principles:**
- **Simplicity over completeness** - Essential patterns, not full API coverage
- **Object-based hierarchy** - Each entity is a Pydantic model
- **Escape hatches** - Always access underlying Playwright objects
- **Type safety** - Leverages Pydantic validation and Python type hints

## Installation
```bash
pip install webdantic
```

Requires Python 3.11+ and Playwright.

## Quick Start
```python
from webdantic import Browser

async with Browser.connect(port=9222) as browser:
    window = await browser.get_window(0)
    tab = await window.new_tab()
    page = await tab.get_page()
    
    await page.goto("https://example.com")
    
    # Type-safe element interaction
    button = await page.select("button.submit")
    await button.click()
    
    # Get element text
    heading = await page.select("h1")
    text = await heading.text()
    print(f"Page title: {text}")
```

## Object Hierarchy
```
Browser (CDP connection manager)
└── Window (browser window/context)
    └── Tab (individual tab)
        └── Page (page interaction wrapper)
            └── Selector (element selection/interaction)
```

Each object:
- Is a Pydantic BaseModel for validation and serialization
- Has a parent reference (except Browser)
- Exposes underlying Playwright object via `playwright_*` property

## Core Objects

### Browser

Manages the Chrome CDP connection and window collection.
```python
# Connect to existing Chrome instance
browser = await Browser.connect(port=9222)

# Access windows
windows = await browser.get_windows()
window = await browser.get_window(0)

# Access raw Playwright browser
raw = browser.playwright_browser

await browser.disconnect()
```

### Window

Represents a browser window/context containing tabs.
```python
# Create new tab
tab = await window.new_tab()

# Get existing tabs
tabs = await window.get_tabs()
active = await window.get_active_tab()

# Window operations
await window.maximize()
await window.minimize()
await window.close()
```

### Tab

Individual tab within a window.
```python
# Navigate
await tab.navigate("https://example.com")

# Activate tab
await tab.activate()

# Get page wrapper
page = await tab.get_page()

# Close tab
await tab.close()
```

### Page

Core interaction layer wrapping Playwright Page.
```python
# Navigation
await page.goto("https://example.com")
await page.wait_for_load_state("networkidle")

# Element selection (returns Selector)
button = await page.select("button#submit")
buttons = await page.select_all("button.action")

# JavaScript evaluation
result = await page.evaluate("() => document.title")

# Screenshots
await page.screenshot(path="screenshot.png")

# Access raw Playwright page
raw_page = page.playwright_page
```

### Selector

Represents selected element(s) with common operations.
```python
# Interaction
await selector.click()
await selector.type("Hello world")
await selector.fill("form input")

# Data extraction
text = await selector.text()
value = await selector.attribute("href")
is_visible = await selector.is_visible()

# Access raw locator
raw_locator = selector.playwright_locator
```

## Features

### Type Safety

All objects are Pydantic models with validation:
```python
from webdantic import Browser, BrowserConfig

config = BrowserConfig(
    port=9222,
    timeout=30000,
    headless=False
)

browser = await Browser.connect(config=config)
```

### Async Context Managers

Clean resource management:
```python
async with Browser.connect(port=9222) as browser:
    async with await browser.get_window(0) as window:
        async with await window.new_tab() as tab:
            page = await tab.get_page()
            await page.goto("https://example.com")
    # Automatically cleaned up
```

### Wait Conditions

Common wait patterns:
```python
# Wait for selector
await page.wait_for_selector("div.content")

# Wait for navigation
await page.wait_for_navigation()

# Wait for custom condition
await page.wait_for_function("() => document.readyState === 'complete'")
```

### Error Handling

Custom exception hierarchy:
```python
from webdantic.exceptions import (
    WebdanticError,
    ConnectionError,
    NavigationError,
    SelectorError,
    TimeoutError
)

try:
    await page.goto("https://example.com")
except NavigationError as e:
    print(f"Failed to navigate: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
```

## Escape Hatches

Every wrapper exposes its underlying Playwright object:
```python
# Browser
playwright_browser = browser.playwright_browser

# Page
playwright_page = page.playwright_page
await playwright_page.evaluate("console.log('direct access')")

# Selector
playwright_locator = selector.playwright_locator
await playwright_locator.highlight()
```

## What's Included

- ✅ Browser connection management (CDP)
- ✅ Window/tab navigation
- ✅ Element selection (CSS, XPath)
- ✅ Common interactions (click, type, fill)
- ✅ Wait conditions
- ✅ JavaScript evaluation
- ✅ Screenshots and PDFs
- ✅ Basic navigation

## What's Not Included (Yet)

- ❌ Network interception/modification
- ❌ Advanced DevTools protocol features
- ❌ Cookie management beyond basics
- ❌ File upload/download
- ❌ Multi-browser support (Firefox, Safari)

## Architecture Decisions

**Why Pydantic?**
- Type safety and validation
- Serialization support
- IDE autocompletion
- Runtime data validation

**Why expose Playwright objects?**
- Avoids reimplementing entire API
- Power users get full access
- Gradual adoption path
- No feature limitations

**Why object hierarchy?**
- Natural mental model
- Clear ownership and lifecycle
- Easy navigation between levels
- Type-safe relationships

## Development
```bash
# Install with UV
uv pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Format
ruff format src/
```

## Examples

See the `examples/` directory for:
- Basic navigation and interaction
- Form filling and submission
- Screenshot capture
- JavaScript evaluation
- Error handling patterns
- Multi-tab workflows

## License

MIT

## Contributing

Contributions welcome! Please:
- Follow the code standards (see CONTRIBUTING.md)
- Keep files under 500 lines
- Add tests for new features
- Update documentation