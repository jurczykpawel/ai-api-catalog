"""
AI API Catalog — REST API
Serwuje dane z data/models.json jako przeszukiwalne API dla agentów.

Uruchomienie:
  pip install fastapi uvicorn
  uvicorn api.main:app --host 0.0.0.0 --port 8001

Lub przez Docker (patrz api/Dockerfile).
"""

import json
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ── Ładowanie danych ───────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"

def load_data():
    with open(DATA_DIR / "models.json") as f:
        models_data = json.load(f)
    with open(DATA_DIR / "providers.json") as f:
        providers_data = json.load(f)
    with open(DATA_DIR / "categories.json") as f:
        categories_data = json.load(f)
    return models_data, providers_data, categories_data

models_data, providers_data, categories_data = load_data()
MODELS: list = models_data["models"]
PROVIDERS: dict = {p["id"]: p for p in providers_data["providers"]}
CATEGORIES: dict = {c["id"]: c for c in categories_data["categories"]}

# ── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI API Catalog",
    description="Katalog modeli AI dostępnych przez API — ceny, dostawcy, możliwości.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Helpers ────────────────────────────────────────────────────────
def get_best_price(model: dict) -> Optional[float]:
    """Zwraca najniższą cenę spośród dostępnych providerów."""
    values = []
    for p in model.get("providers", []):
        if not p.get("available"):
            continue
        pricing = p.get("pricing") or {}
        for key in ("input_per_1m", "per_image", "per_second", "per_video",
                    "per_video_5s", "per_video_6s", "per_minute", "per_megapixel"):
            if key in pricing:
                values.append(pricing[key])
                break
    return min(values) if values else None


def enrich_providers(model: dict) -> list:
    """Dodaje metadane providera do każdego wpisu w providers[]."""
    result = []
    for p in model.get("providers", []):
        pid = p.get("provider_id")
        meta = PROVIDERS.get(pid, {})
        result.append({
            **p,
            "provider_name": meta.get("name", pid),
            "provider_type": meta.get("type", ""),
            "provider_url":  meta.get("url", ""),
        })
    return result


def model_summary(model: dict) -> dict:
    """Lekka wersja modelu do list/search (bez pełnych providerów)."""
    best = get_best_price(model)
    available_count = sum(1 for p in model.get("providers", []) if p.get("available"))
    return {
        "id":               model["id"],
        "name":             model["name"],
        "category":         model.get("category"),
        "description":      model.get("description") or model.get("description_en", ""),
        "capabilities":     model.get("capabilities", []),
        "open_source":      model.get("open_source", False),
        "local_available":  model.get("local_available", False),
        "providers_count":  available_count,
        "best_price":       best,
        "updated_at":       model.get("updated_at"),
    }


def model_detail(model: dict) -> dict:
    """Pełny model z wzbogaconymi providerami."""
    return {
        **model,
        "providers": enrich_providers(model),
        "best_price": get_best_price(model),
    }

# ── Endpoints ──────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "AI API Catalog",
        "models": len(MODELS),
        "providers": len(PROVIDERS),
        "docs": "/docs",
    }


@app.get("/models", summary="Szukaj i filtruj modele")
def list_models(
    q:          Optional[str]  = Query(None,  description="Szukaj po nazwie, opisie lub tagu"),
    category:   Optional[str]  = Query(None,  description="np. video_generation, llm, image_generation"),
    provider:   Optional[str]  = Query(None,  description="ID providera, np. piapi, fal, openai"),
    capability: Optional[str]  = Query(None,  description="np. text_to_video, vision, reasoning"),
    max_price:  Optional[float]= Query(None,  description="Maksymalna najlepsza cena"),
    open_source:Optional[bool] = Query(None,  description="Tylko open-source"),
    sort:       str            = Query("name", description="name | price_asc | price_desc | providers_desc"),
    limit:      int            = Query(50,    ge=1, le=500),
    offset:     int            = Query(0,     ge=0),
):
    result = MODELS

    if q:
        q_lower = q.lower()
        result = [
            m for m in result
            if q_lower in m["name"].lower()
            or q_lower in (m.get("description") or "").lower()
            or q_lower in (m.get("description_en") or "").lower()
            or any(q_lower in tag.lower() for tag in (m.get("tags") or []))
        ]

    if category:
        result = [m for m in result if m.get("category") == category]

    if provider:
        result = [
            m for m in result
            if any(p["provider_id"] == provider for p in m.get("providers", []))
        ]

    if capability:
        result = [m for m in result if capability in (m.get("capabilities") or [])]

    if open_source is not None:
        result = [m for m in result if m.get("open_source") == open_source]

    if max_price is not None:
        filtered = []
        for m in result:
            best = get_best_price(m)
            if best is not None and best <= max_price:
                filtered.append(m)
        result = filtered

    # Sort
    if sort == "price_asc":
        result = sorted(result, key=lambda m: (get_best_price(m) is None, get_best_price(m) or 0))
    elif sort == "price_desc":
        result = sorted(result, key=lambda m: get_best_price(m) or 0, reverse=True)
    elif sort == "providers_desc":
        result = sorted(result, key=lambda m: len(m.get("providers", [])), reverse=True)
    else:
        result = sorted(result, key=lambda m: m["name"].lower())

    total = len(result)
    page  = result[offset: offset + limit]

    return {
        "total":  total,
        "offset": offset,
        "limit":  limit,
        "models": [model_summary(m) for m in page],
    }


@app.get("/models/{model_id}", summary="Szczegóły modelu z pełną listą providerów")
def get_model(model_id: str):
    model = next((m for m in MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' nie znaleziony.")
    return model_detail(model)


@app.get("/providers", summary="Lista wszystkich providerów")
def list_providers():
    return list(PROVIDERS.values())


@app.get("/providers/{provider_id}", summary="Modele dostępne u danego providera")
def get_provider_models(provider_id: str):
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' nie znaleziony.")
    models = [
        model_summary(m)
        for m in MODELS
        if any(p["provider_id"] == provider_id for p in m.get("providers", []))
    ]
    models.sort(key=lambda m: m["name"].lower())
    return {
        "provider":     PROVIDERS[provider_id],
        "models_count": len(models),
        "models":       models,
    }


@app.get("/categories", summary="Lista kategorii z liczbą modeli")
def list_categories():
    counts = {}
    for m in MODELS:
        cat = m.get("category", "unknown")
        counts[cat] = counts.get(cat, 0) + 1

    result = []
    for cat in CATEGORIES.values():
        result.append({
            **cat,
            "models_count": counts.get(cat["id"], 0),
        })
    return result


@app.get("/compare/{model_id}", summary="Porównanie cen modelu u wszystkich providerów")
def compare_prices(model_id: str):
    model = next((m for m in MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' nie znaleziony.")

    providers = []
    for p in model.get("providers", []):
        pid   = p.get("provider_id")
        meta  = PROVIDERS.get(pid, {})
        best  = get_best_price({"providers": [p]})
        providers.append({
            "provider_id":   pid,
            "provider_name": meta.get("name", pid),
            "provider_type": meta.get("type", ""),
            "available":     p.get("available", False),
            "pricing":       p.get("pricing"),
            "best_price":    best,
            "url":           p.get("affiliate_url") or p.get("url"),
            "notes":         p.get("notes"),
        })

    # Sortuj dostępne po cenie
    available   = sorted([p for p in providers if p["available"] and p["best_price"] is not None],
                         key=lambda p: p["best_price"])
    unavailable = [p for p in providers if not p["available"]]
    no_price    = [p for p in providers if p["available"] and p["best_price"] is None]

    if available:
        available[0]["cheapest"] = True

    return {
        "model_id":   model_id,
        "model_name": model["name"],
        "category":   model.get("category"),
        "providers":  available + no_price + unavailable,
    }
