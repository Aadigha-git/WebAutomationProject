"""
Core Playwright automation
"""

import time
import re
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ----------------------------
# Playwright Driver
# ----------------------------
class PlaywrightDriver:
    def __init__(self, headless: bool = True, timeout: int = 10000):
        self.playwright = None
        self.browser = None
        self.page = None
        self.headless = headless
        self.timeout = timeout

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _sanitize_filename(self, s: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]", "_", s)[:120]

    def _take_screenshot(self, name: str):
        filename = f"screenshot_{self._sanitize_filename(name)}_{int(time.time())}.png"
        try:
            self.page.screenshot(path=filename)
            logger.info(f"Saved screenshot: {filename}")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")

    def navigate(self, url: str) -> bool:
        try:
            logger.info(f"Navigating to: {url}")
            resp = self.page.goto(url, wait_until="domcontentloaded")
            if resp and resp.status and resp.status >= 400:
                logger.error(f"HTTP {resp.status} at {url}")
                self._take_screenshot("bad_response")
                return False
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            self._take_screenshot("navigation_error")
            return False

    def click(self, selector: str, retry: int = 3) -> bool:
        for attempt in range(retry):
            try:
                locator = self.page.locator(selector)
                locator.wait_for(state="visible", timeout=self.timeout)
                locator.click()
                return True
            except PlaywrightTimeout:
                logger.warning(f"Timeout waiting for: {selector}")
            except Exception as e:
                logger.error(f"Click failed ({attempt+1}/{retry}): {e}")
            time.sleep(1)
        self._take_screenshot(f"click_error_{selector}")
        return False

    def type_text(self, selector: str, text: str, retry: int = 3) -> bool:
        for attempt in range(retry):
            try:
                locator = self.page.locator(selector)
                locator.wait_for(state="visible", timeout=self.timeout)
                locator.fill(text)
                return True
            except Exception as e:
                logger.error(f"Type failed ({attempt+1}/{retry}): {e}")
            time.sleep(1)
        self._take_screenshot(f"type_error_{selector}")
        return False


# ----------------------------
# Automation Logic
# ----------------------------
class SauceDemoTask:
    URL = "https://www.saucedemo.com/"

    def __init__(self, driver: PlaywrightDriver):
        self.driver = driver

    def run(self) -> str:
        logger.info("Starting SauceDemo task...")
        if not self.driver.navigate(self.URL):
            return "❌ Failed to navigate"

        if not self.driver.type_text("#user-name", "standard_user"):
            return "❌ Failed typing username"
        if not self.driver.type_text("#password", "secret_sauce"):
            return "❌ Failed typing password"
        if not self.driver.click("#login-button"):
            return "❌ Failed clicking login"

        time.sleep(2)
        product_name = "Sauce Labs Backpack"
        price = self._get_product_price(product_name)
        if price:
            result = f"✅ Success! {product_name} costs {price}"
            logger.info(result)
            return result
        return "❌ Product not found"

    def _get_product_price(self, product_name: str) -> str:
        try:
            items = self.driver.page.locator(".inventory_item")
            count = items.count()
            for i in range(count):
                item = items.nth(i)
                name = (item.locator(".inventory_item_name").text_content() or "").strip()
                if name == product_name:
                    price = item.locator(".inventory_item_price").text_content()
                    return price
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
        return None


# ----------------------------
# CLI Entry (local run)
# ----------------------------
def run_automation(goal: str = "default") -> dict:
    """
    Main entry point that runs the Playwright task.
    """
    logger.info(f"Running automation for goal: {goal}")
    with PlaywrightDriver(headless=True) as driver:
        task = SauceDemoTask(driver)
        result = task.run()
    return {"goal": goal, "result": result}


if __name__ == "__main__":
    output = run_automation()
    print(output["result"])


# ----------------------------
# FastAPI Wrapper
# ----------------------------
app = FastAPI(title="Automation API", version="1.0")


class GoalRequest(BaseModel):
    goal: str = "check product price"


@app.post("/run")
async def run_goal(req: GoalRequest):
    """
    POST /run
    Example:
    curl -X POST "http://localhost:8000/run" -H "Content-Type: application/json" -d '{"goal": "check product price"}'
    """
    # Offload to thread so Playwright can run synchronously without blocking the event loop
    result = await asyncio.to_thread(run_automation, req.goal)
    return result
