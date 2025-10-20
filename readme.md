# Playwright Automation with FastAPI

This project demonstrates a robust pattern for running synchronous Playwright browser automation tasks wrapped in an asynchronous FastAPI server. It provides a reusable `PlaywrightDriver` class, a specific automation task (`SauceDemoTask`), and two ways to run the automation: directly via CLI or as a web service.

The example task logs into [saucedemo.com](https://www.saucedemo.com/), finds the price of a "Sauce Labs Backpack," and returns the result.

## ✨ Features

* **Reusable `PlaywrightDriver` Class**: A context-managed (`with ...`) driver that handles browser launch and teardown automatically.
* **Robust Actions**: Helper methods for `Maps`, `click`, and `type_text` with built-in retries and timeouts.
* **Error Handling**: Automatically takes screenshots on navigation, click, or typing failures for easy debugging.
* **Clean Separation**: Business logic (`SauceDemoTask`) is separate from the driver logic (`PlaywrightDriver`).
* **Dual-Mode Operation**:
    * **CLI**: Can be run directly from the command line for testing.
    * **API**: A FastAPI server exposes the automation via a POST endpoint.
* **Async-Safe**: Uses `asyncio.to_thread` to run the synchronous Playwright code in a separate thread, preventing it from blocking the FastAPI event loop.

## 🛠️ Tech Stack

* **Python 3.8+**
* **Playwright**: For browser automation.
* **FastAPI**: For creating the web API.
* **Uvicorn**: As the ASGI server to run FastAPI.

## 🚀 Getting Started

### 1. Setup

**Clone the repository:**
```bash
git clone <your-repo-url>
cd <your-repo-directory>