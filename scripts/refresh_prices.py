#!/usr/bin/env python3
"""Met à jour hébergeurs, prix et couleur Budget depuis l'API publique OpenRouter.

Ne touche qu'aux champs hosts, price_in, price_out, discount, budget de data/models.json,
écrit dans data/warnings.json les modèles introuvables, et liste dans data/candidates.json les modèles récents des éditeurs suivis
(à examiner par la tâche hebdomadaire). Pas de clé requise ; OPENROUTER_API_KEY est
utilisée si présente.

Usage : python3 scripts/refresh_prices.py [data/models.json]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

API = "https://openrouter.ai/api/v1"
VENDORS = ("anthropic/", "openai/", "google/", "mistralai/", "moonshotai/", "z-ai/", "deepseek/")
EXCLUDED_TIERS = {"flex", "priority", "batch"}
PATH = sys.argv[1] if len(sys.argv) > 1 else "data/models.json"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "llm-eu-radar"})
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == 2:
                raise
        except urllib.error.URLError:
            if attempt == 2:
                raise
        time.sleep(2 * (attempt + 1))


def budget(price_out):
    if price_out <= 2.5:
        return "V"
    if price_out <= 8:
        return "O"
    return "R"


def offers_for(model_id, providers):
    data = get(f"{API}/models/{model_id}/endpoints")
    if not data or not data.get("data"):
        return []
    offers = []
    for ep in data["data"].get("endpoints", []):
        tag = (ep.get("tag") or "").lower()
        prefix = tag.split("/")[0]
        if prefix not in providers:
            continue
        tier = (ep.get("service_tier") or "").lower()
        if tier in EXCLUDED_TIERS or any(f"/{t}" in tag for t in EXCLUDED_TIERS):
            continue
        p = ep.get("pricing") or {}
        try:
            pin = float(p.get("prompt")) * 1e6
            pout = float(p.get("completion")) * 1e6
        except (TypeError, ValueError):
            continue
        if pin <= 0 and pout <= 0:
            continue
        offers.append((pin, pout, prefix, float(p.get("discount") or 0)))
    return offers


def summarize(offers, providers):
    if not offers:
        return None
    hosts = sorted({o[2] for o in offers}, key=list(providers).index)
    pin, pout, _, disc = min(offers, key=lambda o: (3 * o[0] + o[1]) / 4)
    return {"hosts": " · ".join(providers[h] for h in hosts),
            "price_in": round(pin, 4), "price_out": round(pout, 4), "discount": disc}


def main():
    d = json.load(open(PATH, encoding="utf-8"))
    providers = d["providers"]
    changes = []
    for m in d["models"]:
        offer = summarize([o for mid in m.get("openrouter_ids", []) for o in offers_for(mid, providers)], providers)
        if not offer:
            changes.append(f"⚠️ {m['model']} : aucun endpoint chez les 5 hébergeurs (valeurs conservées)")
            continue
        new_budget = budget(offer["price_out"])
        for k, v in list(offer.items()) + [("budget", new_budget)]:
            if m.get(k) != v:
                changes.append(f"{m['model']} : {k} {m.get(k)} → {v}")
                m[k] = v

    # Candidats : modèles récents des éditeurs suivis, absents de la liste
    known = {i for m in d["models"] for i in m.get("openrouter_ids", [])}
    cutoff = datetime.now(timezone.utc) - timedelta(days=45)
    candidates = []
    catalog = get(f"{API}/models") or {"data": []}
    for mod in catalog["data"]:
        mid = mod.get("id", "")
        if not mid.startswith(VENDORS) or mid in known or ":" in mid:
            continue
        created = datetime.fromtimestamp(mod.get("created", 0), timezone.utc)
        if created < cutoff:
            continue
        offer = summarize(offers_for(mid, providers), providers)
        if offer:
            candidates.append({"id": mid, "name": mod.get("name"), "created": created.date().isoformat(), **offer})

    if any(not c.startswith("⚠️") for c in changes):
        d["prices_checked"] = date.today().isoformat()
    json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(candidates, open(os.path.join(os.path.dirname(PATH), "candidates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    warnings = [c for c in changes if c.startswith("⚠️")]
    json.dump(warnings, open(os.path.join(os.path.dirname(PATH), "warnings.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n".join(changes) or "Aucun changement de prix.")
    print(f"{len(candidates)} modèle(s) candidat(s) dans candidates.json")


if __name__ == "__main__":
    main()
