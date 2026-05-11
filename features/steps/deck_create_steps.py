import json
import time

from behave import given, when, then

from features.environment import BASE_URL, username, password, COMMANDER_DATA


def _fill_commander_hidden_inputs(context, prefix="commander"):
    # Bypass the live Scryfall AJAX flow by setting the hidden inputs directly
    # to a known Card. Mirrors how card_quantity_steps drives the form via JS.
    fields = {
        "scryfall_id": COMMANDER_DATA["scryfall_id"],
        "oracle_id": COMMANDER_DATA["oracle_id"],
        "name": COMMANDER_DATA["name"],
        "type_line": COMMANDER_DATA["type_line"],
        "image_url": COMMANDER_DATA["image_url"],
        "image_large_url": COMMANDER_DATA["image_large_url"],
        "set_code": COMMANDER_DATA["set_code"],
        "collector_number": COMMANDER_DATA["collector_number"],
        "cmc": COMMANDER_DATA["cmc"],
    }
    lines = [
        f"document.getElementById({json.dumps(f'{prefix}_{k}')}).value = {json.dumps(v)};"
        for k, v in fields.items()
    ]
    context.browser.execute_script("\n".join(lines))


@given("I am logged in")
def step_i_am_logged_in(context):
    context.browser.visit(f"{BASE_URL}/accounts/login/")
    if not context.browser.find_by_name("username"):
        # already authenticated — the login form is not rendered
        return
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_id("login-submit").click()
    time.sleep(1)


@given("I am not logged in")
def step_i_am_not_logged_in(context):
    # Selenium only knows about cookies for domains it has actually visited,
    # so we must land on the target host before clearing the session cookie.
    context.browser.visit(f"{BASE_URL}/")
    context.browser.driver.delete_all_cookies()
    context.browser.visit(f"{BASE_URL}/")


@when("I visit the deck create page")
def step_visit_deck_create_page(context):
    context.browser.visit(f"{BASE_URL}/decks/new/")


@when('I fill the deck form with name "{deck_name}" and a valid commander')
def step_fill_create_form(context, deck_name):
    context.browser.fill("name", deck_name)
    _fill_commander_hidden_inputs(context, "commander")
    context.deck_name = deck_name


@when("I submit the deck form")
def step_submit_deck_form(context):
    # Strip HTML5 'required' first so empty-form scenarios reach Django's
    # server-side validation instead of being blocked by the browser.
    context.browser.execute_script(
        "document.querySelectorAll('#deck-form [required]').forEach("
        "el => el.removeAttribute('required'));"
    )
    context.browser.find_by_css('#deck-form button[type="submit"]').click()
    time.sleep(4)


@then('a deck named "{deck_name}" should exist owned by me')
def step_deck_should_exist(context, deck_name):
    from blog.models import Deck
    from django.contrib.auth.models import User

    user = User.objects.get(username=username)
    assert Deck.objects.filter(name=deck_name, author=user).exists(), (
        f"Deck '{deck_name}' was not created for user '{username}'"
    )


@then("I should still be on the deck create page")
def step_still_on_create_page(context):
    assert "/decks/new/" in context.browser.url, (
        f"Expected to remain on /decks/new/, got: {context.browser.url}"
    )


@then('no deck named "{deck_name}" should exist')
def step_no_deck_should_exist(context, deck_name):
    from blog.models import Deck
    assert not Deck.objects.filter(name=deck_name).exists(), (
        f"Deck '{deck_name}' should not exist"
    )


@then("I should be redirected to the login page")
def step_redirected_to_login(context):
    assert "/accounts/login/" in context.browser.url, (
        f"Expected redirect to /accounts/login/, got: {context.browser.url}"
    )
