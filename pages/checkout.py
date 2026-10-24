from playwright.sync_api import Page, expect


class CheckoutPage:
    """Cart, customer details, order overview and confirmation."""

    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.item_names = page.locator('[data-test="inventory-item-name"]')
        self.error = page.locator('[data-test="error"]')
        self.subtotal = page.locator('[data-test="subtotal-label"]')
        self.tax = page.locator('[data-test="tax-label"]')
        self.total = page.locator('[data-test="total-label"]')
        self.confirmation = page.locator('[data-test="complete-header"]')
        self.badge = page.locator('[data-test="shopping-cart-badge"]')

    def begin(self):
        expect(self.title).to_have_text("Your Cart")
        self.page.get_by_role("button", name="Checkout", exact=True).click()

    def submit_details(self, first="Alex", last="Tester", postal="10115"):
        self.page.get_by_placeholder("First Name").fill(first)
        self.page.get_by_placeholder("Last Name").fill(last)
        self.page.get_by_placeholder("Zip/Postal Code").fill(postal)
        self.page.get_by_role("button", name="Continue", exact=True).click()

    def finish(self):
        self.page.get_by_role("button", name="Finish", exact=True).click()

    def cancel(self):
        self.page.get_by_role("button", name="Cancel", exact=True).click()
