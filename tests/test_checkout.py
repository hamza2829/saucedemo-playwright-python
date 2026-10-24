import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_complete_purchase(checkout):
    expect(checkout.item_names).to_have_text(["Sauce Labs Backpack", "Sauce Labs Bike Light"])
    checkout.begin()
    checkout.submit_details()
    expect(checkout.title).to_have_text("Checkout: Overview")
    expect(checkout.item_names).to_have_text(["Sauce Labs Backpack", "Sauce Labs Bike Light"])
    checkout.finish()
    expect(checkout.confirmation).to_have_text("Thank you for your order!")
    expect(checkout.badge).to_have_count(0)


@pytest.mark.regression
@pytest.mark.parametrize("first,last,postal,message", [
    ("", "Tester", "10115", "First Name is required"),
    ("Alex", "", "10115", "Last Name is required"),
    ("Alex", "Tester", "", "Postal Code is required"),
], ids=["first-name-empty", "last-name-empty", "postal-code-empty"])
def test_missing_checkout_fields(checkout, first, last, postal, message):
    checkout.begin()
    checkout.submit_details(first, last, postal)
    expect(checkout.error).to_have_text("Error: " + message)
    expect(checkout.title).to_have_text("Checkout: Your Information")


@pytest.mark.regression
def test_order_total(checkout):
    checkout.begin()
    checkout.submit_details()
    # Independent expected values: 29.99 + 9.99, then 8% tax rounded to cents.
    expect(checkout.subtotal).to_have_text("Item total: $39.98")
    expect(checkout.tax).to_have_text("Tax: $3.20")
    expect(checkout.total).to_have_text("Total: $43.18")


@pytest.mark.regression
def test_cancel_checkout(checkout):
    checkout.begin()
    checkout.cancel()
    expect(checkout.title).to_have_text("Your Cart")
    expect(checkout.item_names).to_have_text(["Sauce Labs Backpack", "Sauce Labs Bike Light"])
