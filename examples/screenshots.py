#!/usr/bin/env python3

# examples/screenshots.py
"""Screenshot example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/screenshots.py
"""
import asyncio
from pathlib import Path
from webdantic import Browser, ScreenshotConfig


async def main():
    async with await Browser.connect(port=9222) as browser:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()
        
        # Navigate
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot
        output_dir = Path("screenshots")
        output_dir.mkdir(exist_ok=True)
        
        screenshot_path = output_dir / "example.png"
        print(f"Taking screenshot: {screenshot_path}")
        
        config = ScreenshotConfig(full_page=True)
        await page.screenshot(path=screenshot_path, config=config)
        
        print(f"Screenshot saved to {screenshot_path}")
        
        await tab.close()


if __name__ == "__main__":
    asyncio.run(main())