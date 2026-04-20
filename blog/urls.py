from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("decks/", views.DeckListView.as_view(), name="decks"),
    path("decks/<int:pk>/", views.DeckDetailView.as_view(), name="deck_detail"),
    path("your-decks/", views.your_decks, name="your_decks"),
    path("decks/new/", views.DeckCreateView.as_view(), name="deck_create"),
    path("decks/<int:deck_id>/update/<int:card_id>/", views.update_quantity, name="update_quantity"),

    path("decks/<int:deck_id>/delete/", views.delete_deck, name="delete_deck"),
    path("decks/<int:deck_id>/remove/<int:card_id>/", views.remove_card, name="remove_card"),
    path("decks/<int:deck_id>/add-card/", views.add_card, name="add_card"),
]