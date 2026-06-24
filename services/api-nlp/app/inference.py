"""Logique d'inférence pour la classification de sentiment.

Le modèle CamemBERT chargé sort des labels 5 étoiles
(`'1 star'`, `'2 stars'`, ..., `'5 stars'`). Le métier (Aubergine Hôtels)
veut 3 classes (`négatif`, `neutre`, `positif`).

→ Ton travail dans ce fichier :
   1. Implémenter `predict_sentiment()` (récupère scores 5★ + appelle map).
   2. Implémenter `map_stars_to_sentiment()` (mapping 5★ → 3 classes).
   3. Justifier le seuil retenu en commentaire (cf. brief).

Le pipeline transformers est chargé une seule fois au démarrage, dans
`main.py` (lifespan), et stocké dans `state["pipeline"]`. Tu le récupères
en argument.
"""
from __future__ import annotations

import time
from typing import Any

from app.schemas import Sentiment, SentimentOut
from loguru import logger


def map_stars_to_sentiment(scores: dict[str, float]) -> Sentiment:
    """Mappe les scores 5★ en 3 classes métier via moyenne pondérée.

    Stratégie : on calcule la moyenne des probabilités pour chaque groupe
    métier et on retourne la classe dont la moyenne est la plus élevée.
    - négatif  : moyenne(1★, 2★)
    - neutre   : moyenne(2★, 3★, 4★)
    - positif  : moyenne(4★, 5★)

    Args:
        scores: dict label → probabilité produit par le pipeline HF.

    Returns:
        Sentiment 3 classes.
    """
    mean_neg = (scores["1 star"] + scores["2 stars"]) / 2
    mean_neutre = (scores["2 stars"] + scores["3 stars"] + scores["4 stars"]) / 3
    mean_pos = (scores["4 stars"] + scores["5 stars"]) / 2

    best = max(
        [("négatif", mean_neg), ("neutre", mean_neutre), ("positif", mean_pos)],
        key=lambda x: x[1],
    )
    return best[0]


def predict_sentiment(pipeline: Any, text: str, model_name: str) -> SentimentOut:
    """Inférence de sentiment sur un texte FR.

    Args:
        pipeline: pipeline `transformers.pipeline("text-classification", ...)`
            chargé au démarrage de l'API.
        text: texte FR de la review.
        model_name: identifiant HF du modèle (passé pour traçabilité).

    Returns:
        SentimentOut avec sentiment 3 classes, scores 5★ bruts, et latence ms.
    """
    # TODO Tâche 3 — compléter :
    #
    # 1. Mesurer le temps d'inférence (time.perf_counter() avant/après).
    # 2. Appeler `pipeline(text, top_k=None)` pour récupérer toutes les
    #    probabilités (5 entrées, une par étoile).
    # 3. Construire `scores_5_stars: dict[str, float]` à partir du résultat.
    # 4. Identifier le label argmax (la plus haute proba).
    # 5. Appeler `map_stars_to_sentiment(label_argmax)` pour obtenir la
    #    classe métier.
    # 6. Renvoyer un `SentimentOut(...)`.

    logger.info(f"Requête /predict reçue : {text}")
    t0 = time.perf_counter()

    proba_list = pipeline(text, top_k=None)
    scores_5_stars = {item['label']: item['score'] for item in proba_list}
    sentiment = map_stars_to_sentiment(scores_5_stars)

    duree_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"Score 5 stars: {scores_5_stars}, sentiment: {sentiment}, durée: {duree_ms:.1f} ms")

    return SentimentOut(
        sentiment=sentiment,
        scores_5_stars=scores_5_stars,
        model_name=model_name,
        latence_ms=duree_ms,
    )