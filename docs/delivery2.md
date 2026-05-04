# Deliverable 2 — Web Project (UdL, 2025/26)

**Course:** Projecte Web
**Professors:** Roberto Garcia, David Sarrat
**Team:** Carlos Sallán, Maël Dutrey, [3rd member]

## 1. GitHub Public Repository

https://github.com/CarlosSallan/MTG-EDH-Deckbuilder

GitHub user `rogargon` has been added as a collaborator with read access (per the deliverable requirement).

## 2. Test Credentials

The committed `db.sqlite3` ships with the following users:

| Username   | Password      | Role           | Purpose                                  |
|------------|---------------|----------------|------------------------------------------|
| `mael`     | `admin12345`  | Superuser      | Django admin access (`/admin/`)          |
| `testuser` | `testpass123` | Regular user   | End-user testing (matches E2E fixtures)  |

The database also contains a few sample decks and ~13 cards from Scryfall to make the application immediately testable without manual setup.

## 3. Design Decisions

### What changed since Deliverable 1

The first deliverable shipped a basic Django app with the data model (Card / Deck / DeckCard), Django admin, authentication, Docker setup, and read-only browsing. Deliverable 2 layers Web 2.0 features on top:

#### End-user CRUD (no Django admin required)

- **Create deck** — `DeckCreateView` (ClassView + ModelForm via `fields=[...]`). Authenticated users only.
- **Update deck** — `DeckUpdateView` (ClassView + ModelForm). Editable fields: name, description, visibility, commander, partner commander.
- **Delete deck** — `delete_deck` function view, accessible from both deck detail and "Your Decks" list.
- **Add card to deck** — `add_card` with Scryfall AJAX search.
- **Remove card from deck** — `remove_card`.
- **Update card quantity** — `update_quantity` (in-place quantity adjustment).

#### Security restrictions

`DeckUpdateView.get_queryset()` filters on `author=self.request.user`, returning HTTP 404 to any user attempting to edit a deck they do not own. The same pattern is applied to `delete_deck`, `add_card`, `remove_card` and `update_quantity` via `get_object_or_404(Deck, id=..., author=request.user)`. This deliberately returns 404 (not 403) to avoid leaking the existence of other users' private decks.

#### External API integration (Scryfall)

The Scryfall API (https://scryfall.com/docs/api) is consumed entirely client-side via jQuery + AJAX:

- **Commander selection** on `deck_form.html` — autocomplete on `/cards/autocomplete` followed by `/cards/named` to fetch the full card data, populating hidden form fields before submit. Used for both `commander` (required) and `partner_commander` (optional) on **both create AND update** forms.
- **Card search** on `deck_detail.html` — same pattern when adding cards to a deck.

The backend's `_resolve_card_from_post` helper hydrates a local `Card` model from the POSTed Scryfall data (or reuses an existing one matched by `scryfall_id` UUID), so we cache referenced cards locally rather than re-fetching them from Scryfall on every page load.

#### UX improvements

- **Flash messages** via `django.contrib.messages` after every create/update/delete and after card add/remove. Rendered as colored alerts (success/error/warning/info) at the top of every page.
- **Cancel buttons** on create and update forms — Cancel on Create returns to "Your Decks", on Update returns to deck detail.
- **Form error styling** — proper `.form-errors` block (alert-style) for non-field errors, `.error-text` for field errors, instead of inline `style="color:red"`.
- **Edit shortcut** on "Your Decks" list — a ✏️ button next to 🗑 for each deck, so editing is one click away from the list.

#### E2E testing infrastructure

Behave + Splinter + Selenium have been added to the project (`pyproject.toml`). The `features/` directory contains `environment.py` (browser fixture), one initial scenario for unregistered user login, and matching steps. **Additional CRUD scenarios (deck create/update/delete + security restrictions + error handling) are scheduled for the following sprint** — they will plug into the existing infrastructure without any further setup work. The E2E suite is run against a live development server on port 8002.

#### Technical notes

- **ClassView + ModelForm pattern**: the consigne recommends ClassViews and ModelForms. We use `CreateView`/`UpdateView` (ClassViews) with `fields = [...]`, which makes Django auto-generate a ModelForm at runtime. We considered extracting a dedicated `forms.py` for explicitness but did not pursue it: the auto-generated ModelForm already handles validation, the only manual form handling left (`add_card`, `update_quantity`) deals with Scryfall-specific data flowing through hidden inputs that does not map cleanly to a stand-alone ModelForm.
- **No model changes** since Deliverable 1 — all CRUD is implemented on the existing schema. Three migrations exist (`0001_initial`, `0002_card_image_large_url_card_type_line`, `0003_card_cmc`); the latter two were already part of D1.

### Architecture summary

```
blog/
  models.py           Card / Deck / DeckCard
  views.py            ClassViews (Create/Update) + function views (delete, add_card, remove_card, update_quantity)
                      + _resolve_card_from_post helper shared between Create and Update
  urls.py             Routes for all CRUD endpoints
  templates/blog/
    deck_form.html    Reusable for both create and update (shared with AJAX Scryfall integration)
    deck_detail.html  + AJAX card search for adding cards
    your_decks.html   List of the current user's decks with edit/delete shortcuts
features/             Behave + Splinter E2E setup
templates/base.html   Layout + flash-message rendering
```

## 4. Grade Division

All team members have contributed equally to this deliverable; the grade should be divided equally among the three members.

## 5. How to Run

```bash
# Install dependencies (uv)
uv sync

# Apply migrations (the committed db.sqlite3 is already migrated)
uv run python manage.py migrate

# Start the dev server
uv run python manage.py runserver

# Access:
#   - http://127.0.0.1:8000/           — homepage
#   - http://127.0.0.1:8000/decks/     — public deck list
#   - http://127.0.0.1:8000/admin/     — admin panel (mael / admin12345)
```

To run the existing E2E test, start the server on port 8002 in one terminal and run `behave` in another.
