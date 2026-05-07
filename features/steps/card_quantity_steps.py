import time

from behave import *

from features.environment import BASE_URL

valid_username = "testuser"

@given("a deck owned by user")
def step_deck_owned_by_user(context):
    context.browser.visit(
        f"{context.base_url}/decks/{context.deck.id}/"
    )

@when("I change the quantity to zero")
def step_change_quantity_zero(context):
    context.browser.execute_script("""
        const input = document.querySelector('input[name="quantity"]');
        input.value = 0;
        input.form.submit();
    """)

@then("the quantity should not change")
def step_quantity_not_change(context):
    from blog.models import DeckCard

    time.sleep(5)
    deck_card = DeckCard.objects.get(
        deck=context.deck,
        card=context.card
    )
    assert deck_card.quantity == 1

@when("I change the quantity")
def step_change_quantity(context):
    context.browser.execute_script("""
        const input = document.querySelector('input[name="quantity"]');
        input.value = 5;
        input.form.submit();
    """)

@then("the quantity should change")
def step_quantity_change(context):
    from blog.models import DeckCard

    time.sleep(5)
    deck_card = DeckCard.objects.get(
        deck=context.deck,
        card=context.card
    )

    assert deck_card.quantity == 5