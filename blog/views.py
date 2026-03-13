from django.shortcuts import render
# blog/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Deck

class DeckListView(ListView):
    model = Deck
    template_name = "blog/decks.html"
    context_object_name = "decks"

    def get_queryset(self):
        return Deck.objects.filter(is_public=True)
def home(request):
    """Home page view."""
    # request = the incoming HTTP request (URL, method, headers, user info, etc.)
    # render() loads the template file, returns it as an HTTP response
    return render(request, 'blog/home.html')