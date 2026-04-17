# Projecte web – Activity 1

## Github public address

https://github.com/CarlosSallan/MTG-EDH-Deckbuilder

## Design decisions

### 1. Card preview on deck detail

**What we wanted to do:**
- Show a bigger version of the card when you hover over it on deck detail.
- Without JavaScript.
- Making it simple.

**Main idea:**
All big images of a card are shown with an opacity of 0. When you hover over a specific
card, the opacity of the big image of the card passes to have a value of 1.

### 2. Sorting the cards by type

**What we wanted to do:**
- Inside the deck detail, we wanted to show the cards sorted by card type (creature, enchantment, sorcery...)
- Making it simple for possible change in the future as we incorporate an API.

**Main idea:**
In views.py, in the class DeckDetailView the cards are sorted by type so the deck detail
will show them later.

## Grading

| # | Task | Contributors |
|---|------|-------------|
| 1 | Implement the proposed model | Mael, Carlos, Eloy |
| 2 | Activate the Django admin interface | Mael, Carlos |
| 3 | Add user authentication and registration | Mael, Carlos, Eloy |
| 4 | Docker / docker-compose setup | Eloy |
| 5 | 12factor guidelines | Mael, Carlos |
| 6 | (Recommended) Views / templates / browsing | Mael, Carlos |
| 7 | (Recommended) UI design | Mael, Carlos |
