from django.urls import path
from . import views
from .views import DeckListView

urlpatterns = [
    path("", views.home, name="home"),
    path("decks/", DeckListView.as_view(), name="deck_list"),
]