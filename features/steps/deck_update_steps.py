import time

from behave import given, when, then

from features.environment import BASE_URL


@given("a deck I own exists")
def step_my_deck_exists(context):
    assert getattr(context, "user_deck", None) is not None, "user_deck fixture missing"


@given("a deck owned by another user exists")
def step_other_deck_exists(context):
    assert getattr(context, "other_deck", None) is not None, "other_deck fixture missing"


@when("I visit the edit page for my deck")
def step_visit_my_edit_page(context):
    context.browser.visit(f"{BASE_URL}/decks/{context.user_deck.id}/edit/")


@when("I visit the edit page for the other user's deck")
def step_visit_other_edit_page(context):
    context.browser.visit(f"{BASE_URL}/decks/{context.other_deck.id}/edit/")


@when('I change the deck name to "{new_name}" and submit')
def step_change_name_and_submit(context, new_name):
    context.browser.fill("name", new_name)
    context.browser.find_by_css('#deck-form button[type="submit"]').click()
    context.new_deck_name = new_name
    time.sleep(4)


@when("I clear the deck name and submit")
def step_clear_name_and_submit(context):
    context.browser.fill("name", "")
    # Strip HTML5 'required' to exercise Django's server-side validation.
    context.browser.execute_script(
        "document.querySelectorAll('#deck-form [required]').forEach("
        "el => el.removeAttribute('required'));"
    )
    context.browser.find_by_css('#deck-form button[type="submit"]').click()
    time.sleep(4)


@then('the deck name should be "{expected_name}" in the database')
def step_deck_name_should_be(context, expected_name):
    from blog.models import Deck
    deck = Deck.objects.get(id=context.user_deck.id)
    assert deck.name == expected_name, (
        f"Expected deck name '{expected_name}', got '{deck.name}'"
    )


@then("I should see a not-found page")
def step_see_404(context):
    html = (context.browser.html or "").lower()
    assert ("404" in html) or ("not found" in html) or ("page not found" in html), (
        "Expected a 404 page, but the page does not look like one"
    )


@then("the other user's deck should remain unchanged")
def step_other_deck_unchanged(context):
    from blog.models import Deck
    deck = Deck.objects.get(id=context.other_deck.id)
    assert deck.name == "e2e_other_user_deck", (
        f"Other user's deck name was modified: {deck.name}"
    )


@then("I should still be on the deck edit page")
def step_still_on_edit_page(context):
    assert "/edit/" in context.browser.url, (
        f"Expected to remain on edit page, got: {context.browser.url}"
    )


@then("the deck name should remain unchanged")
def step_deck_name_unchanged(context):
    from blog.models import Deck
    deck = Deck.objects.get(id=context.user_deck.id)
    assert deck.name == "e2e_update_deck", (
        f"Expected deck name 'e2e_update_deck', got '{deck.name}'"
    )
