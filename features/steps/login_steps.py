from behave import *

valid_username = "testuser"
invalid_username = "invalid_username"
valid_password = "testpass123"
invalid_password = "invalidpassword123"

@given("a unregistered user")
def step_unregistered_user(context):
    from django.contrib.auth.models import User
    """
    User in not logged in, but there is a valid account for him to register with.
    """
    if not User.objects.filter(username=valid_username).exists():
        User.objects.create_user(
            username=valid_username,
            password=valid_password,
        )


@when("I go to the login page")
def step_go_login(context):
    context.browser.visit("http://127.0.0.1:8002/accounts/login/")


@when("I fill the form with valid credentials of an existing user")
def step_fill_login_form(context):
    context.browser.fill("username", valid_username)
    context.browser.fill("password", valid_password)


@when('I press "Login"')
def step_press_login(context):
    assert isinstance(context.browser.find_by_id("login-submit").click, object)
    context.browser.find_by_id("login-submit").click()


@then("I should logged in")
def step_logged_in(context):
    assert "/accounts/login/" not in context.browser.url # Check if logged in

@when("I fill the form with invalid credentials")
def step_fill_login_form_invalid_credentials(context):
    context.browser.fill("username", valid_username)
    context.browser.fill("password", invalid_password)

@then("the login should fail")
def step_see_login_error_message(context):
    # assert url
    assert "/accounts/login/" in context.browser.url

@Given("a non-existent user")
def step_see_non_existent_user(context):
    from django.contrib.auth.models import User
    """
    User in not in the db.
    """
    assert not User.objects.filter(username=invalid_username).exists()

@When("I fill the form with nonexisting credentials")
def step_fill_login_form_invalid_credentials(context):
    context.browser.fill("username", invalid_username)
    context.browser.fill("password", invalid_password)