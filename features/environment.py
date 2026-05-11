import os
import uuid
import django

from splinter import Browser

# =====================
# CONFIG GLOBAL
# =====================

username = "testuser"
password = "testpass123"
test_deck_name = "test_deck"

# Second user used by Deck Update / Delete security scenarios.
other_username = "otheruser"
other_password = "otherpass123"

BASE_URL = "http://127.0.0.1:8002"

# Scryfall data for the commander used by E2E deck fixtures. Step files import
# this to populate hidden form inputs via JS (avoids depending on the live
# Scryfall API during tests). Kept in sync with the literals in create_deck().
COMMANDER_DATA = {
    "name": "Leonardo da Vinci",
    "scryfall_id": "283d04a5-3639-42de-b940-ffa7e609e527",
    "oracle_id": "92a287a0-b3cc-4040-a530-fb71510cfc67",
    "type_line": "Legendary Creature — Human Artificer",
    "set_code": "ACR",
    "collector_number": "20",
    "cmc": "3",
    "image_url": "https://cards.scryfall.io/small/front/2/8/leo.jpg",
    "image_large_url": "https://cards.scryfall.io/normal/front/2/8/leo.jpg",
}

# Deck names produced by E2E fixtures — cleanup targets these names only so
# any committed demo decks survive a test run.
E2E_DECK_NAMES = (
    "e2e_create_deck",
    "e2e_renamed_deck",
    "e2e_update_deck",
    "e2e_delete_deck",
    "e2e_other_user_deck",
)


# =====================
# SETUP GENERAL
# =====================

def before_all(context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MTG_EDH_BUILDER.settings")
    django.setup()

    context.browser = Browser()
    context.base_url = BASE_URL


def before_feature(context, feature):

    ensure_user_exists()

    if feature.name in ["Deck Update", "Deck Delete"]:
        ensure_other_user_exists()

    if feature.name in ["Logout", "Card Quantity", "Deck Update", "Deck Delete"]:
        log_in(context)

    if feature.name == "Card Quantity":
        create_deck(context)


def before_scenario(context, scenario):
    feature_name = scenario.feature.name

    if feature_name == "Deck Create":
        _clean_e2e_decks()
    elif feature_name == "Deck Update":
        _refresh_deck_fixtures(context, my_deck_name="e2e_update_deck")
    elif feature_name == "Deck Delete":
        _refresh_deck_fixtures(context, my_deck_name="e2e_delete_deck")


def _clean_e2e_decks():
    from blog.models import Deck

    Deck.objects.filter(name__in=list(E2E_DECK_NAMES)).delete()


def after_feature(context, feature):

    if feature.name == "Card Quantity":
        clean_database()

    if feature.name in ["Deck Create", "Deck Update", "Deck Delete"]:
        clean_deck_test_data()


# =====================
# USER SETUP
# =====================

def ensure_user_exists():
    from django.contrib.auth.models import User

    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.save()


def ensure_other_user_exists():
    from django.contrib.auth.models import User

    user, _ = User.objects.get_or_create(username=other_username)
    user.set_password(other_password)
    user.save()


def log_in(context):
    context.browser.visit(f"{context.base_url}/accounts/login/")
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_id("login-submit").click()


# =====================
# TEST DATA SETUP
# =====================

def create_deck(context):
    from django.contrib.auth.models import User
    from blog.models import Deck, Card, DeckCard

    user = User.objects.get(username=username)

    # Commander
    commander, _ = Card.objects.get_or_create(
        name="Leonardo da Vinci",
        defaults={
            "scryfall_id": uuid.UUID("283d04a5-3639-42de-b940-ffa7e609e527"),
            "oracle_id": uuid.UUID("92a287a0-b3cc-4040-a530-fb71510cfc67"),
            "type_line": "Legendary Creature — Human Artificer",
            "set_code": "ACR",
            "collector_number": "20",
            "cmc": 3,
            "image_url": "https://cards.scryfall.io/small/front/2/8/leo.jpg",
            "image_large_url": "https://cards.scryfall.io/normal/front/2/8/leo.jpg",
        }
    )

    # Card
    card_obj, _ = Card.objects.get_or_create(
        name="Sol Ring",
        defaults={
            "scryfall_id": uuid.UUID("870ec754-a76c-40ea-9b81-81b3dca1f62c"),
            "oracle_id": uuid.UUID("6ad8011d-3471-4369-9d68-b264cc027487"),
            "type_line": "Artifact",
            "set_code": "SOC",
            "collector_number": "128",
            "cmc": 1,
            "image_url": "https://cards.scryfall.io/small/front/8/7/sol.jpg",
            "image_large_url": "https://cards.scryfall.io/normal/front/8/7/sol.jpg",
        }
    )

    # Deck
    deck, _ = Deck.objects.get_or_create(
        name=test_deck_name,
        author=user,
        defaults={
            "commander": commander
        }
    )

    # DeckCard (SIEMPRE consistente)
    deck_card, _ = DeckCard.objects.get_or_create(
        deck=deck,
        card=card_obj,
        defaults={
            "quantity": 1,
            "is_commander": False
        }
    )

    # Guardar en context (MUY IMPORTANTE)
    context.deck = deck
    context.card = card_obj
    context.deck_card = deck_card


def _ensure_commander_card():
    from blog.models import Card

    commander, _ = Card.objects.get_or_create(
        name=COMMANDER_DATA["name"],
        defaults={
            "scryfall_id": uuid.UUID(COMMANDER_DATA["scryfall_id"]),
            "oracle_id": uuid.UUID(COMMANDER_DATA["oracle_id"]),
            "type_line": COMMANDER_DATA["type_line"],
            "set_code": COMMANDER_DATA["set_code"],
            "collector_number": COMMANDER_DATA["collector_number"],
            "cmc": int(COMMANDER_DATA["cmc"]),
            "image_url": COMMANDER_DATA["image_url"],
            "image_large_url": COMMANDER_DATA["image_large_url"],
        }
    )
    return commander


def create_deck_for_user(username_str, name):
    from blog.models import Deck
    from django.contrib.auth.models import User

    user = User.objects.get(username=username_str)
    commander = _ensure_commander_card()
    deck, _ = Deck.objects.get_or_create(
        author=user,
        name=name,
        defaults={"commander": commander},
    )
    return deck


def _refresh_deck_fixtures(context, my_deck_name):
    # Per-scenario reset so scenarios in the same feature don't leak state.
    from blog.models import Deck

    Deck.objects.filter(name__in=list(E2E_DECK_NAMES)).delete()

    context.user_deck = create_deck_for_user(username, name=my_deck_name)
    context.other_deck = create_deck_for_user(other_username, name="e2e_other_user_deck")


# =====================
# CLEANUP
# =====================

def clean_database():
    from blog.models import Deck, Card, DeckCard
    from django.contrib.auth.models import User

    DeckCard.objects.all().delete()
    Deck.objects.all().delete()
    Card.objects.all().delete()
    User.objects.filter(username=username).delete()


def clean_deck_test_data():
    # Selective cleanup: only removes E2E-owned decks and the otheruser fixture,
    # leaving any committed demo data intact.
    from blog.models import Deck, DeckCard
    from django.contrib.auth.models import User

    DeckCard.objects.filter(deck__name__in=list(E2E_DECK_NAMES)).delete()
    Deck.objects.filter(name__in=list(E2E_DECK_NAMES)).delete()
    User.objects.filter(username=other_username).delete()
