"""API FastAPI de classification de sentiment FR (Aubergine Hôtels).

Endpoints :
- GET  /health  : statut + booléen `model_loaded`
- GET  /info    : métadonnées modèle (classes natives, classes métier, max length)
- POST /predict : inférence (STUB à compléter par l'apprenant)
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from loguru import logger

from app import inference
from app.schemas import HealthOut, InfoOut, ReviewIn, SentimentOut


# --- Configuration Loguru (compact, lisible pour des apprenants) ---
# Désactive `diagnose` (dump des variables locales dans la traceback) et
# `backtrace` (frames externes des libs). On garde un format standard.
# Pour debugger un cas complexe, repasse à diagnose=True ponctuellement.
logger.remove()
logger.add(sys.stderr, level="INFO", backtrace=False, diagnose=False)


# --- Filtre access log uvicorn : on n'affiche pas les pings healthcheck ---
# Sans ce filtre, le healthcheck Docker (toutes les 30 s) pollue les logs
# avec des `GET /health 200 OK`, ce qui masque les vrais signaux.
class _SkipHealthAccessLogs(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(_SkipHealthAccessLogs())


# --- Variables d'environnement (injectées via `env_file: .env` dans le compose) ---
# Si le .env est absent, Docker Compose plante au démarrage avec
# "env file not found" — l'apprenant a un retour immédiat, pas besoin
# de check côté Python.
MODEL_NAME: str = os.getenv("MODEL_NAME_HF", "cmarkea/distilcamembert-base-sentiment")
MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "2000"))

# Classes natives du modèle CamemBERT-sentiment (5 étoiles)
NATIVE_CLASSES: list[str] = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
# Classes cibles après mapping métier
TARGET_CLASSES: list[str] = ["négatif", "neutre", "positif"]


# état partagé entre routes (rempli au lifespan)
state: dict[str, Any] = {"pipeline": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le pipeline HF au démarrage, libère au shutdown.

    Politique fail-fast : si le chargement échoue (ImportError, modèle
    indisponible, mémoire insuffisante…), on laisse l'exception remonter.
    Uvicorn s'arrête, le conteneur sort en erreur, Docker affiche
    `unhealthy` dans `docker compose ps`. L'apprenant voit immédiatement
    le problème — pas d'API zombie qui répond OK alors que le modèle est
    cassé.
    """
    from transformers import pipeline

    logger.info("Chargement du pipeline HF : {}", MODEL_NAME)
    state["pipeline"] = pipeline(
        task="text-classification",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        top_k=None,
    )
    logger.success("Pipeline chargé. Modèle prêt.")

    yield

    logger.info("Arrêt de l'API. Libération du pipeline.")
    state["pipeline"] = None


app = FastAPI(
    title="FastIA — Aubergine Hôtels (sentiment FR)",
    description=(
        "Service NLP de classification de sentiment FR sur les reviews "
        "clients d'Aubergine Hôtels. Modèle CamemBERT 5★ avec mapping "
        "métier en 3 classes (négatif / neutre / positif)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    """Statut du service.

    Politique fail-fast : si on arrive ici, c'est que le `lifespan` a réussi
    à charger le pipeline (sinon le conteneur aurait crashé au démarrage).
    Le booléen `model_loaded` reflète l'état réel du pipeline en mémoire.
    """
    return HealthOut(
        status="ok",
        model_loaded=state["pipeline"] is not None,
    )


@app.get("/info", response_model=InfoOut)
def info() -> InfoOut:
    """Métadonnées du service (modèle, classes, contraintes)."""
    return InfoOut(
        service="FastIA Aubergine — sentiment FR",
        model_name=MODEL_NAME,
        native_classes=NATIVE_CLASSES,
        target_classes=TARGET_CLASSES,
        max_text_length=MAX_TEXT_LENGTH,
    )


@app.post("/predict", response_model=SentimentOut, status_code=status.HTTP_200_OK)
def predict(payload: ReviewIn) -> SentimentOut:
    """Classifie une review FR en `négatif / neutre / positif`.

    À compléter par l'apprenant — Tâche 3 du brief. Au clone, l'endpoint
    renvoie 501 Not Implemented.
    """
    # Pas de check `model_loaded` ici : politique fail-fast — si le pipeline
    # ne s'est pas chargé, le conteneur a crashé au démarrage et on n'arrive
    # jamais ici. `state["pipeline"]` est donc garanti non-None.
    if len(payload.texte) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Texte trop long (> {MAX_TEXT_LENGTH} caractères).",
        )

    # TODO Tâche 3 — Appeler inference.predict_sentiment() et logger la requête.
    # Pour l'instant, on signale que ce n'est pas implémenté.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Endpoint /predict pas encore implémenté. Voir Tâche 3 du brief "
            "et `app/inference.py`."
        ),
    )
