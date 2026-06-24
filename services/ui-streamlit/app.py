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

import httpx
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
    try:
        with st.spinner("Inférence en cours…"):
            response = httpx.post(
                f"{API_URL}/predict",
                json={"texte": texte},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        st.error("API trop lente (>10s).")
    except httpx.HTTPStatusError as exc:
        st.error(f"HTTP {exc.response.status_code} : {exc.response.text}")
    except httpx.HTTPError as exc:
        st.error(f"Erreur réseau : {exc}")
    else:
        sentiment = data["sentiment"]
        display = {"négatif": st.error, "neutre": st.warning, "positif": st.success}
        display[sentiment](f"Sentiment détecté : **{sentiment}**")
        st.bar_chart(data["scores_5_stars"])
        st.caption(f"Latence : {data['latence_ms']} ms — modèle : {data['model_name']}")


with st.sidebar:
    st.markdown(f"**API URL** : `{API_URL}`")
    try:
        health = httpx.get(f"{API_URL}/health", timeout=2).json()
        if health.get("model_loaded"):
            st.success("API joignable, modèle chargé")
        else:
            st.warning("API joignable, modèle en chargement")
    except httpx.HTTPError:
        st.error("API injoignable")

