# blog/views.py
import json
import urllib.request
from urllib.error import URLError

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from .models import Deck, DeckCard, Card
from .recommendations import get_recommended_cards
import uuid


def _normalize_color_identity(value):
    """Accept a Scryfall array (list/JSON-string) or letter string; return sorted upper letters from WUBRG."""
    if not value:
        return ""
    if isinstance(value, str):
        # Could be JSON like '["W","U"]' or already a string like "WU"
        stripped = value.strip()
        if stripped.startswith("["):
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                value = list(stripped)
        else:
            value = list(stripped)
    letters = {c.upper() for c in value if isinstance(c, str) and c.upper() in "WUBRG"}
    return "".join(sorted(letters))


def _fetch_color_identity_from_scryfall(scryfall_id):
    """Fetch a card's color_identity from Scryfall and return the normalized string. Returns '' on failure."""
    url = f"https://api.scryfall.com/cards/{scryfall_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MTG-EDH-Deckbuilder/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return ""
    return _normalize_color_identity(data.get("color_identity", []))


def _ensure_card_color_identity(card):
    """Make sure `card.color_identity` is populated; refetch from Scryfall if missing. Returns the string."""
    if card.color_identity:
        return card.color_identity
    fetched = _fetch_color_identity_from_scryfall(card.scryfall_id)
    if fetched:
        card.color_identity = fetched
        card.save(update_fields=["color_identity"])
    return card.color_identity


def _resolve_card_from_post(request, prefix):
    """Get or create a Card from POSTed Scryfall hidden inputs prefixed by `prefix`."""
    scryfall_id = request.POST.get(f"{prefix}_scryfall_id")
    if not scryfall_id:
        return None
    card, _ = Card.objects.get_or_create(
        scryfall_id=uuid.UUID(scryfall_id),
        defaults={
            "oracle_id": uuid.UUID(request.POST.get(f"{prefix}_oracle_id")) if request.POST.get(f"{prefix}_oracle_id") else uuid.uuid4(),
            "name": request.POST.get(f"{prefix}_name", ""),
            "type_line": request.POST.get(f"{prefix}_type_line", ""),
            "image_url": request.POST.get(f"{prefix}_image_url", ""),
            "image_large_url": request.POST.get(f"{prefix}_image_large_url", ""),
            "set_code": request.POST.get(f"{prefix}_set_code", ""),
            "collector_number": request.POST.get(f"{prefix}_collector_number", ""),
            "cmc": int(float(request.POST.get(f"{prefix}_cmc", 0))),
            "color_identity": _normalize_color_identity(request.POST.get(f"{prefix}_color_identity", "")),
        }
    )
    return card


# -------------------------
# MIXIN
# -------------------------

class DeckAccessMixin:
    """Control which decks a user can see."""

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Deck.objects.filter(Q(author=user) | Q(is_public=True))

        return Deck.objects.filter(is_public=True)


# -------------------------
# AUTH
# -------------------------

class SignUpView(CreateView):
    """User SignUp view."""
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


# -------------------------
# HOME
# -------------------------

def home(request):
    """Main page."""
    return render(request, "blog/home.html")


# -------------------------
# DECK LIST
# -------------------------

class DeckListView(DeckAccessMixin, ListView):
    """Decks list view."""
    model = Deck
    template_name = "blog/deck_list.html"
    context_object_name = "decks"
    paginate_by = 5


# -------------------------
# USER DECKS
# -------------------------

@login_required
def your_decks(request):
    """Decks owned by user."""
    decks = Deck.objects.filter(author=request.user)
    return render(request, "blog/your_decks.html", {"decks": decks})


# -------------------------
# DECK DETAIL
# -------------------------

# return the primary type of a card, generalizing it's type.
def get_card_type(type_line):
    main = type_line.split("—")[0].strip()

    if "Creature" in main:
        return "Creature"
    if "Artifact" in main:
        return "Artifact"
    if "Enchantment" in main:
        return "Enchantment"
    if "Instant" in main:
        return "Instant"
    if "Sorcery" in main:
        return "Sorcery"
    if "Planeswalker" in main:
        return "Planeswalker"
    if "Land" in main:
        return "Land"

    return "Other"

class DeckDetailView(DetailView):
    model = Deck
    template_name = "blog/deck_detail.html"
    context_object_name = "deck"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deck = self.object

        cards_by_type = {}

        for dc in DeckCard.objects.filter(deck=deck).select_related("card"):
            type_name = get_card_type(dc.card.type_line)

            if type_name not in cards_by_type:
                cards_by_type[type_name] = {
                    "cards": [],
                    "total": 0
                }

            cards_by_type[type_name]["cards"].append(dc)
            cards_by_type[type_name]["total"] += dc.quantity

        context["cards_by_type"] = cards_by_type
        context["is_owner"] = self.request.user == deck.author

        # Bootstrap data for the JS card-search filter (only useful to the owner).
        commander_ci_bootstrap = {
            "commander": {
                "scryfall_id": str(deck.commander.scryfall_id),
                "color_identity": deck.commander.color_identity,
            },
            "partner": None,
        }
        if deck.partner_commander:
            commander_ci_bootstrap["partner"] = {
                "scryfall_id": str(deck.partner_commander.scryfall_id),
                "color_identity": deck.partner_commander.color_identity,
            }
        context["commander_ci_bootstrap"] = commander_ci_bootstrap

        return context

# -------------------------
# CREATE DECK
# -------------------------

class DeckCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new deck view."""
    model = Deck
    fields = ["name", "description"]
    template_name = "blog/deck_form.html"
    success_url = reverse_lazy("blog:decks")
    success_message = "Deck '%(name)s' created."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commanders"] = [
            ("commander", "Commander", True, None),
            ("partner_commander", "Partner Commander (optional)", False, None),
        ]
        context["cancel_url"] = reverse("blog:your_decks")
        return context

    def form_valid(self, form):
        commander = _resolve_card_from_post(self.request, "commander")
        if not commander:
            form.add_error(None, "Please select a commander.")
            return self.form_invalid(form)

        form.instance.author = self.request.user
        form.instance.commander = commander
        form.instance.partner_commander = _resolve_card_from_post(self.request, "partner_commander")
        return super().form_valid(form)

# -------------------------
# UPDATE DECK
# -------------------------

class DeckUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit a deck owned by the current user."""
    model = Deck
    fields = ["name", "description", "is_public"]
    template_name = "blog/deck_form.html"
    success_message = "Deck '%(name)s' updated."

    def get_queryset(self):
        # 404 if the deck is not owned by the current user — also covers "not found"
        return Deck.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse("blog:deck_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commanders"] = [
            ("commander", "Commander", True, self.object.commander),
            ("partner_commander", "Partner Commander (optional)", False, self.object.partner_commander),
        ]
        context["form_title"] = "Edit deck"
        context["submit_label"] = "Save changes"
        context["cancel_url"] = reverse("blog:deck_detail", kwargs={"pk": self.object.pk})
        return context

    def form_valid(self, form):
        commander = _resolve_card_from_post(self.request, "commander")
        if not commander:
            form.add_error(None, "Please select a commander.")
            return self.form_invalid(form)

        form.instance.commander = commander
        form.instance.partner_commander = _resolve_card_from_post(self.request, "partner_commander")
        return super().form_valid(form)


# -------------------------
# Delete deck
# -------------------------
@login_required
def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)
    deck_name = deck.name
    deck.delete()
    messages.success(request, f"Deck '{deck_name}' deleted.")
    return redirect("blog:your_decks")


# -------------------------
# Add card (via Scryfall)
# -------------------------
@login_required
def add_card(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)

    if request.method == "POST":
        scryfall_id = request.POST.get("scryfall_id")
        name = request.POST.get("name")
        type_line = request.POST.get("type_line", "")
        image_url = request.POST.get("image_url", "")
        image_large_url = request.POST.get("image_large_url", "")
        oracle_id = request.POST.get("oracle_id", "")
        set_code = request.POST.get("set_code", "")
        collector_number = request.POST.get("collector_number", "")
        cmc = int(float(request.POST.get("cmc", 0)))
        color_identity = _normalize_color_identity(request.POST.get("color_identity", ""))

        if scryfall_id and name:
            # Color identity validation: the card's identity must be a subset of
            # the union of commander(s) identities. Empty identity (colorless) is always allowed.
            allowed = set(_ensure_card_color_identity(deck.commander))
            if deck.partner_commander:
                allowed |= set(_ensure_card_color_identity(deck.partner_commander))
            card_colors = set(color_identity)
            forbidden = card_colors - allowed
            if forbidden:
                messages.error(
                    request,
                    f"'{name}' cannot be added: its color identity ({color_identity or 'colorless'}) "
                    f"is outside the commander's identity ({''.join(sorted(allowed)) or 'colorless'})."
                )
                return redirect("blog:deck_detail", pk=deck_id)

            card, _ = Card.objects.get_or_create(
                scryfall_id=uuid.UUID(scryfall_id),
                defaults={
                    "oracle_id": uuid.UUID(oracle_id) if oracle_id else uuid.uuid4(),
                    "name": name,
                    "type_line": type_line,
                    "image_url": image_url,
                    "image_large_url": image_large_url,
                    "set_code": set_code,
                    "collector_number": collector_number,
                    "cmc": cmc,
                    "color_identity": color_identity,
                }
            )
            deck_card, created = DeckCard.objects.get_or_create(deck=deck, card=card)
            if not created:
                deck_card.quantity += 1
                deck_card.save()
            messages.success(request, f"'{name}' added to the deck.")

    return redirect("blog:deck_detail", pk=deck_id)


# -------------------------
# Delete card
# -------------------------
@login_required
def remove_card(request, deck_id, card_id):
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)

    deck_card = get_object_or_404(DeckCard, deck=deck, card_id=card_id)
    card_name = deck_card.card.name
    deck_card.delete()

    messages.success(request, f"'{card_name}' removed from the deck.")
    return redirect("blog:deck_detail", pk=deck.id)

@login_required
def deck_recommendations(request, deck_id):
    """JSON endpoint returning EDHREC-driven recommended cards for the deck."""
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)

    allowed_ci = _ensure_card_color_identity(deck.commander)
    if deck.partner_commander:
        allowed_ci += _ensure_card_color_identity(deck.partner_commander)
    allowed_ci = "".join(sorted(set(allowed_ci)))

    cards = get_recommended_cards(deck, limit=20, allowed_ci=allowed_ci)
    return JsonResponse({"cards": cards})


@require_POST
@login_required
def update_quantity(request, deck_id, card_id):
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)
    deck_card = get_object_or_404(DeckCard, deck=deck, card_id=card_id)

    quantity = int(request.POST.get("quantity", 1))

    if quantity > 0:
        deck_card.quantity = quantity
        deck_card.save()

    return redirect("blog:deck_detail", pk=deck.id)