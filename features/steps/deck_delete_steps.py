import time

from behave import when, then

from features.environment import BASE_URL


@when("I visit the delete URL for my deck")
def step_visit_my_delete_url(context):
    context.deck_id_before_delete = context.user_deck.id
    context.browser.visit(f"{BASE_URL}/decks/{context.user_deck.id}/delete/")
    time.sleep(3)


@when("I visit the delete URL for the other user's deck")
def step_visit_other_delete_url(context):
    context.browser.visit(f"{BASE_URL}/decks/{context.other_deck.id}/delete/")
    time.sleep(3)


@then("my deck should be removed from the database")
def step_my_deck_removed(context):
    from blog.models import Deck
    assert not Deck.objects.filter(id=context.deck_id_before_delete).exists(), (
        "My deck should have been deleted"
    )


@then("the other user's deck should still exist in the database")
def step_other_deck_still_exists(context):
    from blog.models import Deck
    assert Deck.objects.filter(id=context.other_deck.id).exists(), (
        "Other user's deck should still exist"
    )
