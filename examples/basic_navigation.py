#!/usr/bin/env python3

# examples/basic_navigation.py
"""Basic navigation example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/basic_navigation.py
"""
import asyncio
from webdantic import Browser
from time import sleep


async def main():
    # Connect to Chrome
    async with await Browser.connect(port=9222) as browser:
        print("Connected to browser")
        
        # Get first window
        window = await browser.get_window(0)
        print("Got window")
        sleep(1)
        
        # Create new tab
        tab = await window.new_tab()
        print("Created new tab")
        sleep(1)
        
        # Get page wrapper
        page = await tab.get_page()
        sleep(1)
        
        # Navigate
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        sleep(1)
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"Title: {title}")
        print(f"URL: {url}")
        sleep(1)
        
        # Select and interact with elements
        heading = await page.select("h1")
        heading_text = await heading.text()
        print(f"Heading: {heading_text}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Close tab
        await tab.close()
        print("Tab closed")
    
    print("Browser disconnected")


if __name__ == "__main__":
    asyncio.run(main())