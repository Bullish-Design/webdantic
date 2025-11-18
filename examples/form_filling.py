#!/usr/bin/env python3

# examples/form_filling.py
"""Form filling example.

Prerequisites:
1. Start Chrome with CDP enabled:
   chrome --remote-debugging-port=9222
2. Run this script:
   uv run examples/form_filling.py
"""
import asyncio
from webdantic import Browser


async def main():
    async with await Browser.connect(port=9222) as browser:
        window = await browser.get_window(0)
        tab = await window.new_tab()
        page = await tab.get_page()
        
        # Navigate to a page with forms (example)
        print("Navigating to form page...")
        await page.goto("https://httpbin.org/forms/post")
        
        # Fill in form fields
        print("Filling form...")
        
        # Type into text input
        customer_name = await page.select("input[name='custname']")
        await customer_name.fill("John Doe")
        
        # Type into textarea
        comments = await page.select("textarea[name='comments']")
        await comments.fill("This is a test comment")
        
        print("Form filled successfully")
        
        # Wait to see results
        await asyncio.sleep(3)
        
        await tab.close()


if __name__ == "__main__":
    asyncio.run(main())