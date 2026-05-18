# blog/recommendations.py
"""EDHREC-driven recommendation engine for EDH decks.

Aggregates the "Top Cards" list from EDHREC for each card in a deck, with
weighting:
- commander         x3
- partner commander x2
- other deck cards  x1

EDHREC's Next.js JSON endpoint is used directly (pyedhrec doesn't expose the
per-card endpoint). The buildId rotates on every EDHREC deploy, so we discover
it on first call and cache for 24h.
"""
from __future__ import annotations

import json
import re
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError

from django.core.cache import cache

EDHREC_HOME = "https://edhrec.com"
SCRYFALL_COLLECTION = "https://api.scryfall.com/cards/collection"
USER_AGENT = "MTG-EDH-Deckbuilder/1.0"
HTTP_TIMEOUT = 8
ONE_DAY = 24 * 3600

BUILD_ID_CACHE_KEY = "edhrec:build_id"


def _http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8")


def _get_build_id() -> str | None:
    cached = cache.get(BUILD_ID_CACHE_KEY)
    if cached:
        return cached
    try:
        html = _http_get(EDHREC_HOME)
    except (URLError, TimeoutError):
        return None
    m = re.search(r'"buildId":"([^"]+)"', html)
    if not m:
        return None
    build_id = m.group(1)
    cache.set(BUILD_ID_CACHE_KEY, build_id, ONE_DAY)
    return build_id


def _slugify(name: str) -> str:
    """Convert a card name to its EDHREC URL slug.

    DFCs: only the first face is used (the second name 404s on EDHREC).
    """
    first_face = name.split("//")[0].strip()
    return first_face.lower().replace(" ", "-").replace("'", "").replace(",", "")


def _fetch_top_cards(name: str, kind: str) -> list[dict]:
    """Return the `topcards` cardviews for an EDHREC page.

    kind: "commanders" for commander pages, "cards" for any-card pages.
    Cached 24h per (kind, slug). Empty list on 404 / network failure.
    """
    slug = _slugify(name)
    cache_key = f"edhrec:topcards:{kind}:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    build_id = _get_build_id()
    if not build_id:
        return []

    url = f"{EDHREC_HOME}/_next/data/{build_id}/{kind}/{slug}.json"
    try:
        raw = _http_get(url)
    except HTTPError:
        # 404 = card not on EDHREC. Cache as empty so we don't retry every reload.
        cache.set(cache_key, [], ONE_DAY)
        return []
    except (URLError, TimeoutError):
        # Transient network issue — don't poison the cache.
        return []

    try:
        data = json.loads(raw)
        cardlists = data["pageProps"]["data"]["container"]["json_dict"]["cardlists"]
    except (json.JSONDecodeError, KeyError, TypeError):
        cache.set(cache_key, [], ONE_DAY)
        return []

    top = []
    for section in cardlists:
        if section.get("tag") == "topcards":
            for cv in section.get("cardviews", []):
                rec_name = cv.get("name")
                if rec_name:
                    top.append({"name": rec_name, "num_decks": cv.get("num_decks", 0)})
            break

    cache.set(cache_key, top, ONE_DAY)
    return top


def _aggregate_candidates(deck) -> list[tuple[str, int]]:
    """Return [(name, score), ...] sorted desc, excluding cards already in deck."""
    from .models import DeckCard

    deck_card_names: set[str] = {deck.commander.name}
    if deck.partner_commander:
        deck_card_names.add(deck.partner_commander.name)

    tasks: list[tuple[str, str, int]] = [(deck.commander.name, "commanders", 3)]
    if deck.partner_commander:
        tasks.append((deck.partner_commander.name, "commanders", 2))

    for dc in DeckCard.objects.filter(deck=deck).select_related("card"):
        deck_card_names.add(dc.card.name)
        if dc.card.id == deck.commander.id:
            continue
        if deck.partner_commander and dc.card.id == deck.partner_commander.id:
            continue
        tasks.append((dc.card.name, "cards", 1))

    def _run(task):
        name, kind, weight = task
        return weight, _fetch_top_cards(name, kind)

    counter: Counter = Counter()
    with ThreadPoolExecutor(max_workers=8) as ex:
        for weight, recs in ex.map(_run, tasks):
            for r in recs:
                counter[r["name"]] += weight

    for name in deck_card_names:
        counter.pop(name, None)

    return counter.most_common()


def _scryfall_collection_by_name(names: list[str]) -> dict[str, dict]:
    """Fetch Scryfall card objects in bulk by exact name. Returns {name: card}."""
    result: dict[str, dict] = {}
    for i in range(0, len(names), 75):  # Scryfall caps identifiers at 75
        chunk = names[i:i + 75]
        payload = json.dumps({"identifiers": [{"name": n} for n in chunk]}).encode("utf-8")
        req = urllib.request.Request(
            SCRYFALL_COLLECTION,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (URLError, TimeoutError, HTTPError, json.JSONDecodeError):
            continue
        for card in data.get("data", []):
            result[card["name"]] = card
    return result


def _extract_card_payload(card: dict) -> dict:
    """Pull the fields the add-card form needs out of a Scryfall card object."""
    uris = card.get("image_uris") or {}
    if not uris and card.get("card_faces"):
        uris = card["card_faces"][0].get("image_uris") or {}
    ci_letters = "".join(sorted(
        c.upper() for c in (card.get("color_identity") or []) if c.upper() in "WUBRG"
    ))
    return {
        "name": card["name"],
        "scryfall_id": card["id"],
        "oracle_id": card.get("oracle_id", ""),
        "type_line": card.get("type_line", ""),
        "set_code": card.get("set", ""),
        "collector_number": card.get("collector_number", ""),
        "cmc": int(card.get("cmc") or 0),
        "color_identity": ci_letters,
        "image_url": uris.get("small", ""),
        "image_large_url": uris.get("normal", ""),
    }


def get_recommended_cards(deck, limit: int = 20, allowed_ci: str = "") -> list[dict]:
    """Top recommendations for `deck`, enriched with Scryfall data.

    `allowed_ci` (string of letters from WUBRG) is the deck's combined commander
    color identity; recommendations whose identity isn't a subset are dropped.
    Pass "" to skip CI filtering.
    """
    # Over-fetch — some candidates may be filtered out by CI or fail Scryfall lookup.
    candidates = _aggregate_candidates(deck)[: limit * 2]
    if not candidates:
        return []

    sf_data = _scryfall_collection_by_name([name for name, _ in candidates])
    allowed = set(allowed_ci)

    results: list[dict] = []
    for name, score in candidates:
        card = sf_data.get(name)
        if not card:
            continue
        payload = _extract_card_payload(card)
        if allowed_ci and not set(payload["color_identity"]).issubset(allowed):
            continue
        payload["score"] = score
        results.append(payload)
        if len(results) >= limit:
            break
    return results
