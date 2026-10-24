from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.submit = page.get_by_role("button", name="Login", exact=True)
        self.error = page.locator('[data-test="error"]')

    def open(self):
        self.page.goto("https://www.saucedemo.com/")

    def login(self, username="standard_user", password="secret_sauce"):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
