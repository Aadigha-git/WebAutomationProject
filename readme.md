# Playwright Automation 

This project that controls a web browser using Playwright to complete a fixed, single task.

The example task logs into [saucedemo.com](https://www.saucedemo.com/), finds the price of a "Sauce Labs Backpack," and returns the result.
This implements the core requirement. Optional challenges will be updated.


## Tech Stack

* **Python 3.12.3**
* **Playwright**: For browser automation.



## Setup

**Clone the repository:**
Download the repository and navigate into the folder



**Create and activate a virtual environment:**
```bash
python -m venv venv
(Windows) `.\venv\Scripts\activate`
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Install Playwright Browsers**
```bash
playwright install chromium
```

**Run main.py**

## Test Cases
* Navigation:
    - test_navigate_success: Verifies the driver can navigate to given valid URL.
    - test_navigate_failure: Ensures that the driver handles and reports errors for invalid or inaccessible URLs.

* Interaction:
    - test_click_success: Confirms that the driver can locate and click a visible element.
    - test_click_failure: Checks that the driver correctly handles attempts to click non-existent or hidden elements.

* End-to-end flow
    - test_successful_login_and_price_check: Ensures the entire workflow executes correctly: navigates, logs in, and retrieves the specified product's price.

