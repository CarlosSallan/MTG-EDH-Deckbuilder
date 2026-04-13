# blog/models.py

from django.contrib.auth.models import User  # Django's built-in user model
from django.db import models

class Card(models.Model):
    scryfall_id = models.UUIDField(unique=True)
    oracle_id = models.UUIDField()

    name = models.CharField(max_length=200)
    type_line = models.CharField(max_length=200, default='')
    set_code = models.CharField(max_length=10)
    collector_number = models.CharField(max_length=20)

    image_url = models.URLField() # default image size
    image_large_url = models.URLField(default='') # larger image for hover

    def __str__(self):
        return self.name

class Deck(models.Model):
    """EDH Deck Model"""

    # Identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Ownership and visibility
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)

    # Commander(s)
    commander = models.ForeignKey(
        Card, on_delete=models.PROTECT,
        related_name='commander', help_text="First commander")
    partner_commander = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='commander_partner',
        help_text="Second commander if both have partner"
    )

    # Deck stats
    card_count = models.PositiveSmallIntegerField(default=0)
    avg_cmc = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Deck'
        verbose_name_plural = 'Decks'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name = 'unique_deck_name_per_user'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.commander})"

class DeckCard(models.Model):
    """"""
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    is_commander = models.BooleanField(default=False)
    class Meta:
        unique_together = ['deck', 'card']