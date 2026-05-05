import time
from asyncio import wait

from behave import *

valid_username = "testuser"

@given("a registered user")
def registered_user(context):
    from django.contrib.auth.models import User
    """
    User exists and is logged in.
    """
    assert User.objects.filter(username=valid_username).exists()
    print("El nombre es: ",context.browser.find_by_id("logged-user-name").text)
    loged_username = context.browser.find_by_id("logged-user-name").text
    assert loged_username == valid_username
@when('press "Logout"')
def step_logout(context):
    time.sleep(2.5)
    context.browser.find_by_id("logout-btn").click()

@then("should be logged out")
def step_check_logout(context):
    assert context.browser.find_by_id("login-btn")
    assert context.browser.find_by_id("signup-btn")