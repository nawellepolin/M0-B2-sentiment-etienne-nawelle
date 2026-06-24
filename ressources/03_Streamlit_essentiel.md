# Streamlit — Mini-cours

> Brief associé : M0-B2
> Durée de lecture : ~25 min
> Pré-requis : Python 3.11, notions HTTP (requête / réponse / JSON)

## Pourquoi cette techno ?

Construire une UI web complète en React + Node + bundling pour démontrer
un service IA à un client métier est **disproportionné**. Tu veux 1 champ
de saisie, 1 bouton, 1 zone de résultat. Pas un projet front-end de
3 semaines.

**Streamlit** est un framework Python orienté **data apps** : tu écris
ton UI comme un script Python, Streamlit s'occupe du rendu HTML, du
state management et du re-run automatique à chaque interaction. 50 lignes
de Python = une UI démontrable, pas une « POC PowerPoint ».

Cible : data scientists, intégrateurs IA, équipes internes qui ont besoin
d'**itérer vite** sur des UI démo / outillage interne. Pas un framework
pour des produits publics scale ; mais idéal pour M0-B2.

Alternatives :
- **Gradio** : très similaire, plus orienté ML/HF (intégration native
  des modèles HF). Bon choix aussi, on aurait pu prendre l'un ou l'autre.
- **Dash** (Plotly) : plus puissant mais plus complexe.
- **FastAPI + HTML templates** : flexible mais demande du HTML/CSS manuel.
- **React + API** : la prod, pas la démo.

Dans M0-B2, l'UI Streamlit consomme l'API NLP via HTTP (`httpx`). Elle
sert deux usages : démo client métier, et outillage interne pour tester
le modèle sur des reviews avant un déploiement.

## Concepts clés

- **Script-as-app** : Streamlit re-exécute **le script entier** à chaque
  interaction. Pas de routes, pas de framework MVC. Le code lit comme un
  notebook qui s'exécute de haut en bas.

  Concrètement, la timeline d'une frappe utilisateur :

  ```
  1. user tape une lettre dans st.text_area
  2. → Streamlit relance le script ENTIER de haut en bas
  3. → st.text_area renvoie la nouvelle valeur du champ
  4. → la condition `if st.button(...)` est ré-évaluée (False ici)
  5. → l'UI est re-rendue avec la nouvelle valeur du texte
  ```

  C'est pour ça que **toute la logique métier doit être dans un
  `if st.button(...)`** : sinon elle s'exécute à chaque frappe.

- **Streamlit ≠ async** : Streamlit est essentiellement synchrone.
  Inutile d'introduire `asyncio` ou `httpx.AsyncClient` côté UI — tu
  gagneras zéro performance et tu complexifieras le code pour rien.
  Le client `httpx` sync suffit largement pour des appels au bouton.
- **Widgets** : `st.text_area`, `st.button`, `st.selectbox`… renvoient
  une valeur à chaque re-run (le texte saisi, l'état du bouton, l'option
  sélectionnée). Tu chaînes ta logique sur ces valeurs.
- **`st.session_state`** : pour conserver de l'état **entre les re-runs**
  (par ex. l'historique des prédictions, un compteur). Sans ça, tout est
  réinitialisé à chaque clic.
- **Layout** : `st.sidebar`, `st.columns`, `st.expander` permettent de
  structurer la page sans HTML/CSS manuel.
- **Affichage riche** : `st.success`, `st.warning`, `st.error` pour des
  encadrés colorés ; `st.bar_chart`, `st.line_chart` pour des graphes
  simples ; `st.json`, `st.code` pour des dumps techniques.

## Exemple minimal qui tourne

```python
# app.py
import os
import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Sentiment FR", page_icon="🍆")
st.title("🍆 Aubergine Hôtels — sentiment FR")

texte = st.text_area(
    "Texte de la review",
    height=150,
    placeholder="Personnel charmant, chambre impeccable…",
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
    except httpx.HTTPError as exc:
        st.error(f"Erreur API : {exc}")
    else:
        sentiment = data["sentiment"]
        display = {"négatif": st.error, "neutre": st.warning, "positif": st.success}
        display[sentiment](f"Sentiment détecté : **{sentiment}**")
        st.bar_chart(data["scores_5_stars"])
        st.caption(f"Latence : {data['latence_ms']} ms — modèle : {data['model_name']}")
```

Lancement :

```bash
streamlit run app.py
# Browse: http://localhost:8501
```

Dans M0-B2, Streamlit tourne dans son propre conteneur Docker — pas besoin
de l'installer localement.

## Exercice guidé

Dans `services/ui-streamlit/app.py` du squelette, complète la logique du
bouton « Analyser ». 4 TODO listés en haut du fichier :

1. **Appeler l'API** via `httpx.post(f"{API_URL}/predict", json={...},
   timeout=10)`. L'URL `API_URL` vient de la variable d'environnement
   injectée par compose (`http://api-nlp:8000`).
2. **Gérer les erreurs** :
   - `httpx.TimeoutException` → message « API trop lente, réessaie »
   - `httpx.HTTPStatusError` (500, 503, etc.) → message brut + statut
   - `httpx.HTTPError` (catch-all) → message générique
3. **Afficher le sentiment** avec une couleur :
   - `négatif` → `st.error(...)`
   - `neutre` → `st.warning(...)`
   - `positif` → `st.success(...)`
4. **Afficher les scores 5 étoiles bruts** dans un graphe :
   `st.bar_chart(data["scores_5_stars"])`

<details><summary>▶ Voir la solution complète (à dérouler seulement après avoir essayé)</summary>

```python
if st.button("Analyser", type="primary", disabled=not texte.strip()):
    try:
        with st.spinner("Inférence…"):
            r = httpx.post(f"{API_URL}/predict", json={"texte": texte}, timeout=10)
        r.raise_for_status()
        data = r.json()
    except httpx.TimeoutException:
        st.error("⏱️ API trop lente (>10s). Réessaie ou vérifie le service.")
    except httpx.HTTPStatusError as exc:
        st.error(f"HTTP {exc.response.status_code} : {exc.response.text}")
    except httpx.HTTPError as exc:
        st.error(f"Erreur réseau : {exc}")
    else:
        # Affichage sentiment
        sentiment = data["sentiment"]
        display = {"négatif": st.error, "neutre": st.warning, "positif": st.success}
        display[sentiment](f"Sentiment détecté : **{sentiment}**")
        # Probas brutes 5★
        st.bar_chart(data["scores_5_stars"])
        st.caption(f"Latence : {data['latence_ms']:.1f} ms — modèle : {data['model_name']}")
```

</details>

Bonus : ajoute un `st.sidebar` qui affiche `API_URL` et un statut « API
joignable » (ping `/health` au démarrage du script).

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| `httpx.post(f"http://localhost:8000/predict")` depuis le conteneur UI | `Connection refused` — il faut `http://api-nlp:8000` (nom de service docker) |
| Oublier le `timeout` sur `httpx.post` | UI qui freeze si l'API plante ; par défaut httpx attend 5 s puis crash |
| Mettre la logique métier sans `if st.button(...)` | Re-exécutée à **chaque** changement de widget (chaque frappe sur le texte !) |
| Modifier des variables Python en attendant la persistance | Streamlit re-exécute tout, les variables sont réinitialisées. Utilise `st.session_state`. |
| Afficher une exception avec `print()` ou `raise` | Crash brut côté UI, mauvaise expérience. Utilise `st.error(...)`. |
| Re-télécharger un modèle dans Streamlit | Anti-pattern — Streamlit n'est pas un serveur de modèle, il consomme une API |

Symptôme → cause probable :

| Symptôme | Cause probable |
|---|---|
| UI affiche `Connection refused` | URL API mal pointée (nom de service docker manquant) |
| UI freeze 5-10 s avant erreur | Timeout par défaut httpx, `connection refused` masqué |
| Texte affiché doublement | Tu as appelé `st.write(...)` en dehors d'un `if`, donc à chaque re-run |
| Le bouton se déclenche tout seul à chaque frappe | Pas de `if st.button(...)` autour de la logique |
| `st.session_state` non persisté entre runs | Tu modifies une variable locale et pas `st.session_state["..."]` |
| Erreur `httpx.ConnectError` random | Le service `api-nlp` est en cours de démarrage (lifespan) — utilise un `depends_on: condition: service_healthy` |

## Pour aller plus loin

- Doc officielle Streamlit : <https://docs.streamlit.io>
- Cheat sheet (API en 1 page) : <https://docs.streamlit.io/library/cheatsheet>
- Gallery (exemples) : <https://streamlit.io/gallery>
- Tutoriel data app de bout en bout : <https://docs.streamlit.io/get-started/tutorials>
- Repo de référence : <https://github.com/streamlit/streamlit/tree/master/examples>
- **Repo multi-page Streamlit + LLM** (utile pour comprendre `st.Page`,
  `st.navigation` et l'organisation d'une app à plusieurs vues — préfigure
  ce qu'on fera en M7-B2) : <https://github.com/streamlit/llm-examples>
- **Doc OPCO ATLAS legacy** (~1620 mots, plus détaillé) : disponible **à
  la demande sur Discord** auprès de Marianne

## Vérification (checklist apprenant)

- [ ] J'ai compris que Streamlit re-exécute **tout le script** à chaque
      interaction (et pourquoi `if st.button(...)` est essentiel)
- [ ] J'ai branché mon UI à l'API du squelette via `http://api-nlp:8000`
      (pas `localhost`) et `httpx` avec un `timeout=10`
- [ ] L'UI affiche le sentiment avec une couleur différenciée
      (rouge / orange / vert) selon la classe retournée
- [ ] L'UI affiche un message clair si l'API est down ou répond une erreur
      (pas une stack trace brute)
- [ ] J'ai testé manuellement avec 3-4 reviews du `data/sample_reviews.csv`
      pour valider le rendu
