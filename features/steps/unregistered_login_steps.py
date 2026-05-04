from behave import *


@given("a unregistered user")
def step_unregistered_user(context):
    from django.contrib.auth.models import User
    """
    User in not logged in, but there is a valid account for him to register with.
    """
    if not User.objects.filter(username="testuser").exists():
        User.objects.create_user(
            username="testuser",
            password="testpass123"
        )


@when("I go to the login page")
def step_go_login(context):
    context.browser.visit("http://127.0.0.1:8002/accounts/login/")


@when("I fill the form with valid credentials of an existing user")
def step_fill_login_form(context):
    context.browser.fill("username", "testuser")
    context.browser.fill("password", "testpass123")


@when('I press "Login"')
def step_press_login(context):
    assert isinstance(context.browser.find_by_id("login-submit").click, object)
    context.browser.find_by_id("login-submit").click()


@then("I should logged in")
def step_logged_in(context):
    assert context.browser.url != "http://127.0.0.1:8002/accounts/login/" # Check if logged in