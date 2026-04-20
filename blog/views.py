# blog/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Deck, DeckCard


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

class DeckDetailView(DeckAccessMixin, DetailView):
    """Deck detail view with cards grouped by type."""
    model = Deck
    template_name = "blog/deck_detail.html"
    context_object_name = "deck"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # All cards of the deck
        deck_cards = self.object.deckcard_set.select_related("card").all()

        # Dictionary: type → cards of the type
        cards_by_type = {}
        for dc in deck_cards:
            card_type = dc.card.type_line or "Other"
            if card_type not in cards_by_type:
                cards_by_type[card_type] = []
            cards_by_type[card_type].append(dc)

        type_order = ["Battle", "Planeswalker", "Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Land", "Other"]
        sorted_cards = {k: cards_by_type[k] for k in type_order if k in cards_by_type}
        context["cards_by_type"] = sorted_cards
        return context

# -------------------------
# CREATE DECK
# -------------------------

class DeckCreateView(LoginRequiredMixin, CreateView):
    """Create a new deck view."""
    model = Deck
    fields = ["name", "commander", "description"]
    template_name = "blog/deck_form.html"
    success_url = reverse_lazy("blog:decks")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# -------------------------
# Delete card
# -------------------------
@login_required
def remove_card(request, deck_id, card_id):
    deck = get_object_or_404(Deck, id=deck_id, author=request.user)

    deck_card = get_object_or_404(DeckCard, deck=deck, card_id=card_id)

    deck_card.delete()

    return redirect("blog:deck_detail", pk=deck.id)

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