import pytest
from playwright.sync_api import expect

from pages.inventory import InventoryPage


@pytest.mark.smoke
def test_valid_login(login, page):
    login.login()
    InventoryPage(page).ready()


@pytest.mark.regression
def test_invalid_password(login):
    login.login(password="incorrect_password")
    expect(login.error).to_have_text("Epic sadface: Username and password do not match any user in this service")


@pytest.mark.regression
def test_locked_out_user(login):
    login.login(username="locked_out_user")
    expect(login.error).to_have_text("Epic sadface: Sorry, this user has been locked out.")


@pytest.mark.regression
@pytest.mark.parametrize("username,password,message", [
    ("", "", "Username is required"),
    ("", "secret_sauce", "Username is required"),
    ("standard_user", "", "Password is required"),
], ids=["both-empty", "username-empty", "password-empty"])
def test_empty_login_fields(login, username, password, message):
    login.login(username, password)
    expect(login.error).to_have_text("Epic sadface: " + message)
