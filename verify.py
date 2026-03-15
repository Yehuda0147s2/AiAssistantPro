from playwright.sync_api import sync_playwright
import os
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Correct path
        path = os.path.abspath("impervo-comers-pro/dist/index.html")
        print(f"Loading: file://{path}")
        page.goto(f"file://{path}")

        # Wait for module loading
        time.sleep(2)

        # Verify basic elements
        title = page.locator("#page-title")
        if title.is_visible():
            print(f"Page title: {title.inner_text()}")
        else:
            print("Title not found")

        # Screenshot
        os.makedirs("/home/jules/verification", exist_ok=True)
        page.screenshot(path="/home/jules/verification/verification.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
