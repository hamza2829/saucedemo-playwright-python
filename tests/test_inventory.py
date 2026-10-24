import pytest
from playwright.sync_api import expect

NAMES = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt", "Sauce Labs Fleece Jacket", "Sauce Labs Onesie", "Test.allTheThings() T-Shirt (Red)"]


@pytest.mark.regression
@pytest.mark.parametrize("sort_value,field,expected", [
    ("az", "product_names", NAMES),
    ("za", "product_names", list(reversed(NAMES))),
    ("lohi", "product_prices", ["$7.99", "$9.99", "$15.99", "$15.99", "$29.99", "$49.99"]),
    ("hilo", "product_prices", ["$49.99", "$29.99", "$15.99", "$15.99", "$9.99", "$7.99"]),
], ids=["name-ascending", "name-descending", "price-ascending", "price-descending"])
def test_sorting(inventory, sort_value, field, expected):
    inventory.sort(sort_value)
    expect(getattr(inventory, field)).to_have_text(expected)


@pytest.mark.smoke
def test_add_to_cart(inventory):
    inventory.add(NAMES[0])
    expect(inventory.remove_button(NAMES[0])).to_be_visible()
    expect(inventory.badge).to_have_text("1")


@pytest.mark.regression
def test_remove_from_cart(inventory):
    inventory.add(NAMES[0])
    inventory.remove(NAMES[0])
    expect(inventory.add_button(NAMES[0])).to_be_visible()
    expect(inventory.badge).to_have_count(0)


@pytest.mark.regression
@pytest.mark.parametrize("count", [1, 3])
def test_cart_badge_count(inventory, count):
    for name in NAMES[:count]:
        inventory.add(name)
    expect(inventory.badge).to_have_text(str(count))
