from django.contrib import admin
from .models import Card, Deck, DeckCard


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "set_code", "collector_number", "scryfall_id")
    search_fields = ("name", "set_code", "collector_number")
    list_filter = ("set_code",)


class DeckCardInline(admin.TabularInline):
    model = DeckCard
    extra = 1


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "commander", "is_public", "card_count", "updated_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("name", "author__username")
    inlines = [DeckCardInline]


@admin.register(DeckCard)
class DeckCardAdmin(admin.ModelAdmin):
    list_display = ("deck", "card", "quantity", "is_commander")
    list_filter = ("is_commander",)
    search_fields = ("deck__name", "card__name")