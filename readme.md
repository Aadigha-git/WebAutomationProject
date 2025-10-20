# Playwright Automation with FastAPI

This project demonstrates a robust pattern for running synchronous Playwright browser automation tasks wrapped in an asynchronous FastAPI server. It provides a reusable `PlaywrightDriver` class, a specific automation task (`SauceDemoTask`), and two ways to run the automation: directly via CLI or as a web service.

The example task logs into [saucedemo.com](https://www.saucedemo.com/), finds the price of a "Sauce Labs Backpack," and returns the result.


## 🛠️ Tech Stack

* **Python 3.8+**
* **Playwright**: For browser automation.


## Getting Started

### 1. Setup

**Clone the repository:**
```bash
git clone <your-repo-url>
cd <your-repo-directory>

**Create and activate a virtual environment:**
python -m venv venv
On Windows, use `.\venv\Scripts\activate`

**Install dependencies**
pip install -r requirements.txt

**Install Playwright Browsers**
playwright install chromium

**Run main.py**