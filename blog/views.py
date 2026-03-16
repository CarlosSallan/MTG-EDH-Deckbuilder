from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
# blog/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Deck

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
        return Deck.objects.filter(is_public=True)
def home(request):
    """Home page view."""
    # request = the incoming HTTP request (URL, method, headers, user info, etc.)
    # render() loads the template file, returns it as an HTTP response
    return render(request, 'blog/home.html')

class DeckDetailView(DetailView):
    model = Deck
    template_name = "blog/deck_detail.html"
    context_object_name = "deck"