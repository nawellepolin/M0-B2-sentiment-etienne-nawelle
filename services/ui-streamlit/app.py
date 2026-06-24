"""UI Streamlit pour le service NLP Aubergine Hôtels.

Au clone, l'UI s'affiche mais ne consomme PAS encore l'API. À toi de :

1. Implémenter l'appel à `POST /predict` via httpx (Tâche 4 du brief).
2. Gérer les erreurs (API down, timeout 10 s).
3. Afficher le sentiment avec une couleur selon la classe :
   - 🔴 négatif → couleur rouge
   - 🟠 neutre  → couleur orange
   - 🟢 positif → couleur verte
4. Afficher les probabilités 5 étoiles brutes en barres (st.bar_chart).

L'URL de l'API est dans la variable d'environnement `API_URL`
(injectée par docker-compose, vaut `http://api-nlp:8000`).
"""
from __future__ import annotations

import os

import streamlit as st


API_URL: str = os.getenv("API_URL", "http://api-nlp:8000")


st.set_page_config(
    page_title="Aubergine Hôtels — sentiment FR",
    page_icon="🍆",
    layout="centered",
)

st.title("🍆 Aubergine Hôtels — qualification du sentiment")
st.caption(
    "Démo interne : copie une review FR, le service NLP renvoie son sentiment "
    "en 3 classes (négatif / neutre / positif)."
)

texte = st.text_area(
    "Texte de la review",
    height=150,
    placeholder="Ex : Personnel charmant, chambre impeccable, on reviendra !",
)

if st.button("Analyser", type="primary", disabled=not texte.strip()):
    # TODO Tâche 4 — Implémenter l'appel HTTP à POST {API_URL}/predict
    #
    # Indications :
    # - Utilise httpx (déjà dans requirements.txt).
    # - Timeout 10 s.
    # - En cas d'erreur réseau ou HTTP >= 500 : affiche un message d'erreur
    #   clair via st.error("...").
    # - Affiche le sentiment dans un encadré coloré (st.success / st.warning /
    #   st.error selon la classe).
    # - Affiche les scores 5 étoiles bruts via st.bar_chart().
    st.info("📡 Appel API à implémenter — Tâche 4 du brief M0-B2.")
    st.code(
        f'httpx.post("{API_URL}/predict", json={{"texte": "..."}}, timeout=10)',
        language="python",
    )

with st.sidebar:
    st.markdown(f"**API URL** : `{API_URL}`")
    st.markdown(
        "**Statut** : à brancher (Tâche 4).\n\n"
        "Une fois branchée, l'UI doit afficher :\n"
        "- Le sentiment (3 classes)\n"
        "- Les probas 5★ brutes\n"
        "- Un message d'erreur clair si l'API tombe"
    )