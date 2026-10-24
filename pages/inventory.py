from playwright.sync_api import Page, expect


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.products = page.locator('[data-test="inventory-item"]')
        self.product_names = page.locator('[data-test="inventory-item-name"]')
        self.product_prices = page.locator('[data-test="inventory-item-price"]')
        self.badge = page.locator('[data-test="shopping-cart-badge"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.sort_control = page.locator('[data-test="product-sort-container"]')

    def ready(self):
        expect(self.title).to_have_text("Products")
        expect(self.products).to_have_count(6)

    def product(self, name):
        return self.products.filter(has=self.page.get_by_text(name, exact=True))

    def add(self, name):
        self.product(name).get_by_role("button", name="Add to cart", exact=True).click()

    def remove(self, name):
        self.product(name).get_by_role("button", name="Remove", exact=True).click()

    def remove_button(self, name):
        return self.product(name).get_by_role("button", name="Remove", exact=True)

    def add_button(self, name):
        return self.product(name).get_by_role("button", name="Add to cart", exact=True)

    def sort(self, value):
        self.sort_control.select_option(value)

    def open_cart(self):
        self.cart_link.click()
