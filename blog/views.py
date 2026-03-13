from django.shortcuts import render
from django.views.generic import ListView
from .models import Deck


def home(request):
    return render(request, template_name='blog/home.html')


class DeckListView(ListView):
    model = Deck
    template_name = "blog/deck_list.html"
    context_object_name = "decks"