from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
# blog/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Deck
#-----------------
# Authentication
#-----------------
class SignUpView(CreateView):
    form_class = UserCreationForm                  # the form to show (username + password + confirm)
    template_name = 'registration/signup.html'     # the HTML template to render
    success_url = reverse_lazy('login')            # after signup, redirect to the login page

class DeckListView(ListView):
    model = Deck
    template_name = "blog/deck_list.html"
    context_object_name = "decks"
    paginate_by = 5

    def get_queryset(self):
        user=self.request.user
        if user.is_authenticated:
            return Deck.objects.filter(Q(author=user) | Q(is_public=True))
        else:
            return Deck.objects.filter(is_public=True)
#-----------
# Home
#-----------
def home(request):
    """Home page view."""
    # request = the incoming HTTP request (URL, method, headers, user info, etc.)
    # render() loads the template file, returns it as an HTTP response
    return render(request, 'blog/home.html')

@login_required
def your_decks(request):
    decks = Deck.objects.filter(author=request.user)
    return render(request, "blog/your_decks.html", {"decks": decks})

class DeckDetailView(DetailView):
    model = Deck
    template_name = "blog/deck_detail.html"
    context_object_name = "deck"

#------------
# Mixin
#-------------
class DeckVisibilityMixin:
    """ Mixin for viewing Decks that are yours or public """
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Deck.objects.filter(Q(author=user) | Q(is_public=True))
        else:
            return Deck.objects.filter(is_public=True)

class DeckCreateView(CreateView):
    model = Deck
    fields = ["name", "commander", "description"]
    template_name = "blog/deck_form.html"
    success_url = reverse_lazy("blog:decks")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        return Deck.objects.filter(is_public=True)

#------------
# Deck List
#------------
class DeckListView(DeckVisibilityMixin, ListView):
    model = Deck
    template_name = "blog/decks.html"
    context_object_name = "decks"

#-------------
# Deck Detail
#-------------
class DeckDetailView(DeckVisibilityMixin, DetailView):
    model = Deck
    template_name = "blog/deck_detail.html"
    context_object_name = "deck"
