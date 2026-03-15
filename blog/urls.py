from django.urls import path

from . import views
app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path("decks/", views.DeckListView.as_view(), name="decks"),
]