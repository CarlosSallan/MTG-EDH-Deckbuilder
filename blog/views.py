from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.db.models import Q
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

#-----------
# Home
#-----------
def home(request):
    """Home page view."""
    # request = the incoming HTTP request (URL, method, headers, user info, etc.)
    # render() loads the template file, returns it as an HTTP response
    return render(request, 'blog/home.html')

#------------
# Mixin
#-------------
class DeckVisibilityMixin:
    """ Mixin for viewing Decks that are yours or public """
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Deck.objects.filter(Q(author=user) | Q(is_public=True))
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