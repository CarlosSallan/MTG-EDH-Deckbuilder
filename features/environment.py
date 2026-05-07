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

BASE_URL = "http://127.0.0.1:8002"


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

    if feature.name in ["Logout", "Card Quantity"]:
        log_in(context)

    if feature.name == "Card Quantity":
        create_deck(context)


def after_feature(context, feature):

    if feature.name == "Card Quantity":
        clean_database()


# =====================
# USER SETUP
# =====================

def ensure_user_exists():
    from django.contrib.auth.models import User

    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
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