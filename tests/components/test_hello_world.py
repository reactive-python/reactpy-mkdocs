from typing import Callable
from playwright.sync_api import Page


def test_simple(page: Page) -> None:
    page.wait_for_selector("#hello-world", timeout=1000)
