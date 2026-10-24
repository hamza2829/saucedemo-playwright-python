import base64
import hashlib
from pathlib import Path

import pytest
import pytest_html
from playwright.sync_api import expect

from pages.checkout import CheckoutPage
from pages.inventory import InventoryPage
from pages.login import LoginPage


def pytest_addoption(parser):
    parser.addoption("--artifact-dir", default="test-results", help="Failure PNG and trace directory")


@pytest.fixture
def page(browser, browser_name, request):
    """Fresh storage per test; retain screenshot and trace only for failures."""
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    context.set_default_timeout(10_000)
    context.set_default_navigation_timeout(30_000)
    expect.set_options(timeout=10_000)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    digest = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:10]
    folder = Path(request.config.getoption("--artifact-dir")) / browser_name / (request.node.originalname + "-" + digest)
    request.node.failure_page = page
    request.node.failure_folder = folder
    yield page
    try:
        failed = any(getattr(request.node, "rep_" + phase, None) and getattr(request.node, "rep_" + phase).failed for phase in ("setup", "call"))
        if failed:
            folder.mkdir(parents=True, exist_ok=True)
            context.tracing.stop(path=folder / "trace.zip")
        else:
            context.tracing.stop()
    finally:
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    if report.failed and report.when in ("setup", "call"):
        page = getattr(item, "failure_page", None)
        if page is not None and not page.is_closed():
            folder = item.failure_folder
            folder.mkdir(parents=True, exist_ok=True)
            try:
                png = page.screenshot(path=folder / "failure.png", full_page=True, timeout=5000)
                report.extras = getattr(report, "extras", []) + [pytest_html.extras.png(base64.b64encode(png).decode(), name="Failure screenshot")]
            except Exception as exc:
                report.sections.append(("Screenshot capture error", str(exc)))


@pytest.fixture
def login(page):
    result = LoginPage(page)
    result.open()
    return result


@pytest.fixture
def inventory(login, page):
    login.login()
    result = InventoryPage(page)
    result.ready()
    return result


@pytest.fixture
def checkout(inventory, page):
    inventory.add("Sauce Labs Backpack")
    inventory.add("Sauce Labs Bike Light")
    inventory.open_cart()
    return CheckoutPage(page)
