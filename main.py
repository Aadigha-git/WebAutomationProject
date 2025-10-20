# main.py - Core Required Implementation
"""
Playwright Web Automation - Core Implementation
Automates login and product search on Sauce Demo
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PlaywrightDriver:
    """Wrapper for Playwright browser automation with error handling"""
    
    def __init__(self, headless: bool = False, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
        self.page = None
        
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        logger.info("Browser initialized successfully")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")
        
    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """Navigate to URL with error handling"""
        try:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until=wait_until)
            logger.info(f"Successfully loaded: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            self._take_screenshot("navigation_error")
            return False
            
    def click(self, selector: str, retry: int = 3) -> bool:
        """Click element with retries"""
        for attempt in range(retry):
            try:
                logger.info(f"Clicking: {selector} (attempt {attempt + 1}/{retry})")
                self.page.wait_for_selector(selector, state="visible")
                self.page.click(selector)
                logger.info(f"Successfully clicked: {selector}")
                return True
            except PlaywrightTimeout:
                logger.warning(f"Timeout waiting for: {selector}")
                if attempt == retry - 1:
                    self._take_screenshot(f"click_timeout_{selector.replace('#', '').replace('.', '')}")
            except Exception as e:
                logger.error(f"Click failed: {str(e)}")
                if attempt == retry - 1:
                    self._take_screenshot("click_error")
        return False
        
    def type_text(self, selector: str, text: str, retry: int = 3) -> bool:
        """Type text into element with retries"""
        for attempt in range(retry):
            try:
                logger.info(f"Typing into: {selector}")
                self.page.wait_for_selector(selector, state="visible")
                self.page.fill(selector, text)
                logger.info(f"Successfully typed into: {selector}")
                return True
            except PlaywrightTimeout:
                logger.warning(f"Timeout waiting for: {selector}")
                if attempt == retry - 1:
                    self._take_screenshot("type_timeout")
            except Exception as e:
                logger.error(f"Type failed: {str(e)}")
                if attempt == retry - 1:
                    self._take_screenshot("type_error")
        return False
        
    def get_text(self, selector: str, retry: int = 3) -> Optional[str]:
        """Extract text from element"""
        for attempt in range(retry):
            try:
                logger.info(f"Getting text from: {selector}")
                self.page.wait_for_selector(selector, state="visible")
                text = self.page.text_content(selector)
                logger.info(f"Successfully extracted text: {text}")
                return text
            except PlaywrightTimeout:
                logger.warning(f"Timeout waiting for: {selector}")
                if attempt == retry - 1:
                    self._take_screenshot("get_text_timeout")
            except Exception as e:
                logger.error(f"Get text failed: {str(e)}")
                if attempt == retry - 1:
                    self._take_screenshot("get_text_error")
        return None
        
    def wait_for_selector(self, selector: str, state: str = "visible") -> bool:
        """Wait for element to appear"""
        try:
            logger.info(f"Waiting for selector: {selector}")
            self.page.wait_for_selector(selector, state=state)
            return True
        except PlaywrightTimeout:
            logger.error(f"Timeout waiting for selector: {selector}")
            self._take_screenshot("wait_timeout")
            return False
            
    def _take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        try:
            filename = f"screenshot_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.page.screenshot(path=filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")


class SauceDemoTask:
    """Task executor for Sauce Demo automation"""
    
    def __init__(self, driver: PlaywrightDriver):
        self.driver = driver
        self.base_url = "https://www.saucedemo.com"
        
    def execute(self) -> Dict[str, Any]:
        """Execute the main task"""
        logger.info("=== Starting Sauce Demo Task ===")
        
        result = {
            "success": False,
            "message": "",
            "data": {}
        }
        
        # Step 1: Navigate to site
        if not self.driver.navigate(self.base_url):
            result["message"] = "Failed to navigate to website"
            return result
            
        # Step 2: Login
        if not self._login("standard_user", "secret_sauce"):
            result["message"] = "Login failed"
            return result
            
        # Step 3: Find product and get price
        product_name = "Sauce Labs Backpack"
        price = self._get_product_price(product_name)
        
        if price:
            result["success"] = True
            result["message"] = f"Successfully found product: {product_name}"
            result["data"] = {
                "product": product_name,
                "price": price
            }
            logger.info(f"Task completed successfully! Product: {product_name}, Price: {price}")
        else:
            result["message"] = f"Failed to find product: {product_name}"
            
        return result
        
    def _login(self, username: str, password: str) -> bool:
        """Perform login"""
        logger.info(f"Attempting login as: {username}")
        
        # Type username
        if not self.driver.type_text("#user-name", username):
            return False
            
        # Type password
        if not self.driver.type_text("#password", password):
            return False
            
        # Click login button
        if not self.driver.click("#login-button"):
            return False
            
        # Wait for products page
        if not self.driver.wait_for_selector(".inventory_list"):
            logger.error("Products page did not load")
            return False
            
        logger.info("Login successful")
        return True
        
    def _get_product_price(self, product_name: str) -> Optional[str]:
        """Find product and extract price"""
        logger.info(f"Looking for product: {product_name}")
        
        try:
            # Find all product items
            items = self.driver.page.query_selector_all(".inventory_item")
            logger.info(f"Found {len(items)} products")
            
            for item in items:
                name_elem = item.query_selector(".inventory_item_name")
                if name_elem and name_elem.text_content() == product_name:
                    price_elem = item.query_selector(".inventory_item_price")
                    if price_elem:
                        price = price_elem.text_content()
                        logger.info(f"Found product {product_name} with price {price}")
                        return price
                        
            logger.warning(f"Product not found: {product_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding product: {str(e)}")
            self.driver._take_screenshot("product_search_error")
            return None


def main():
    """Main entry point"""
    print("=" * 60)
    print("Playwright Web Automation - Sauce Demo")
    print("=" * 60)
    
    try:
        # Initialize driver with context manager
        with PlaywrightDriver(headless=False, timeout=30000) as driver:
            # Create and execute task
            task = SauceDemoTask(driver)
            result = task.execute()
            
            # Print results
            print("\n" + "=" * 60)
            if result["success"]:
                print("✅ SUCCESS!")
                print(f"Product: {result['data']['product']}")
                print(f"Price: {result['data']['price']}")
            else:
                print("❌ FAILED!")
                print(f"Reason: {result['message']}")
            print("=" * 60)
            
            return 0 if result["success"] else 1
            
    except KeyboardInterrupt:
        logger.info("Task interrupted by user")
        print("\n⚠️  Task interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)