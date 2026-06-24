# Intégration API HTTP (httpx) — Mini-cours

> Brief associé : M0-B2
> Durée de lecture : ~25 min
> Pré-requis : Python 3.11, notions HTTP (méthode, statut, headers, JSON)

## Pourquoi cette techno ?

Quand deux services Python se parlent en HTTP — comme l'UI Streamlit qui
consomme l'API NLP — tu ne veux pas réinventer la gestion des timeouts,
retries, sérialisation JSON, ou des exceptions réseau. Une **bibliothèque
client HTTP** s'en charge.

**`httpx`** est le client HTTP moderne de l'écosystème Python : API
identique à `requests` (familière pour 90 % des devs Python), mais avec
support **async** natif, HTTP/2, et types-friendly. C'est ce qu'utilise
FastAPI sous le capot pour ses propres clients de test (`TestClient`).

Alternatives :
- **`requests`** : standard historique, sync-only, pas d'HTTP/2. Toujours
  bon en 2026 pour des scripts simples.
- **`aiohttp`** : async-first, plus low-level. Bien pour des cas pointus.
- **`urllib`** (stdlib) : API verbeuse, pas d'API moderne. Évite hors
  contraintes très spécifiques (image minimale Docker sans deps).

Dans M0-B2, on utilise `httpx` en **mode synchrone** côté UI Streamlit
(qui est synchrone par nature). Pas besoin d'async ici — on appelle
l'API au clic d'un bouton, pas dans un loop concurrentiel.

## Concepts clés

- **Timeout** : durée maximale d'attente d'une réponse. **Indispensable**
  sur tout appel réseau — sans, l'UI peut freeze indéfiniment. Convention :
  10 s pour des appels lents (modèles ML), 2-5 s pour des APIs rapides.
- **`response.raise_for_status()`** : lève `HTTPStatusError` si le statut
  est 4xx/5xx. Pratique pour mutualiser le traitement d'erreur en un
  seul `try/except`.
- **Hiérarchie d'exceptions** :
  - `httpx.HTTPError` = base de toutes les erreurs httpx
  - `httpx.RequestError` = échec côté requête (réseau, timeout, DNS)
    - `httpx.TimeoutException` = timeout dépassé
    - `httpx.ConnectError` = connexion refusée
  - `httpx.HTTPStatusError` = réponse 4xx/5xx (avec `.response.status_code`)
- **Sérialisation JSON** : `json={...}` envoie un body JSON et positionne
  `Content-Type: application/json`. `response.json()` parse la réponse.
  Plus propre que `data=json.dumps(...)` + header manuel.
- **`with httpx.Client() as client`** : pour des appels multiples, réutilise
  la connexion TCP (gain de perf). Pas indispensable pour 1 appel isolé.
- **Sync vs async** : `httpx` propose un client `Client` (sync) et
  `AsyncClient` (async). Dans M0-B2, on utilise **uniquement le sync** —
  Streamlit est synchrone, l'async n'apporte rien et complique le code.
  L'async deviendra pertinent en M5/M6 quand on parlera de scaling
  serveur (FastAPI peut servir plusieurs requêtes en parallèle).

### Retry ≠ timeout — ne pas confondre

Deux notions souvent mélangées par les débutants :

| Notion | Question | Outil typique |
|---|---|---|
| **Timeout** | Combien de temps j'accepte d'attendre une réponse ? | `httpx.post(..., timeout=10)` |
| **Retry** | Combien de fois je réessaie si l'appel échoue ? | `tenacity` (décorateur `@retry`) |

Le timeout est intégré à `httpx`. Les retries ne le sont **pas** —
`httpx` ne ré-essaie jamais tout seul. Si tu veux des retries, il faut
les ajouter explicitement, typiquement avec `tenacity` ou une boucle
maison. En M0-B2, **pas besoin de retries** : si l'API est down,
l'utilisateur le voit immédiatement (message d'erreur clair) et
réessaie manuellement. Les retries reviendront en M5/M6 quand on
parlera de résilience et de tolérance aux pannes.

## Exemple minimal qui tourne

```python
# /tmp/call_api.py
import httpx

API_URL = "http://localhost:8000"

try:
    response = httpx.post(
        f"{API_URL}/predict",
        json={"texte": "Hôtel impeccable, on reviendra !"},
        timeout=10,
    )
    response.raise_for_status()
except httpx.TimeoutException:
    print("⏱️  Timeout : l'API a mis plus de 10 s.")
except httpx.ConnectError:
    print("🔌 Connexion refusée : l'API tourne-t-elle ?")
except httpx.HTTPStatusError as exc:
    print(f"❌ HTTP {exc.response.status_code} : {exc.response.text}")
else:
    data = response.json()
    print(f"Sentiment : {data['sentiment']}")
    print(f"Latence : {data['latence_ms']} ms")
```

Lancement (avec la stack M0-B2 démarrée) :

```bash
python /tmp/call_api.py
```

Pattern multi-appels (préférer dans une UI qui ping fréquemment l'API) :

```python
with httpx.Client(base_url=API_URL, timeout=10) as client:
    health = client.get("/health").json()
    info = client.get("/info").json()
    prediction = client.post("/predict", json={"texte": "..."}).json()
```

## Exercice guidé

Dans `services/ui-streamlit/app.py` du squelette M0-B2, complète le bloc
`if st.button(...)` pour appeler `/predict` avec une gestion d'erreur
complète :

1. **Appel POST** avec `timeout=10` vers `{API_URL}/predict`
2. **`raise_for_status()`** pour intercepter les 4xx/5xx
3. **3 except** distincts :
   - `httpx.TimeoutException` → message « API trop lente, réessaie »
   - `httpx.HTTPStatusError` → afficher `status_code` et `response.text`
   - `httpx.HTTPError` (catch-all) → message générique
4. **`else`** : extraire `data["sentiment"]`, `data["scores_5_stars"]`,
   `data["latence_ms"]`, et appeler les widgets Streamlit (cf. mini-cours
   `03_Streamlit_essentiel.md`).

<details><summary>▶ Voir la solution complète (à dérouler seulement après avoir essayé)</summary>

```python
import httpx
import streamlit as st

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
    # afficher le sentiment, les scores, la latence (cf. mini-cours 03)
    ...
```

</details>

Bonus : ajoute un **ping `/health`** au démarrage de l'UI pour afficher
en sidebar « ✅ API joignable » ou « ❌ API down ». Comme l'UI va aussi
appeler `/predict` ensuite, c'est l'occasion de réutiliser un
`httpx.Client` avec `base_url` (gain : la connexion TCP est partagée
entre les 2 appels) :

```python
with httpx.Client(base_url=API_URL, timeout=2) as client:
    try:
        healthy = client.get("/health").json().get("model_loaded")
        st.sidebar.success("✅ API joignable" if healthy else "⚠️ API en chargement")
    except httpx.HTTPError:
        st.sidebar.error("❌ API down")
```

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Pas de `timeout` | UI freeze 30 s à 5 min si l'API plante (timeout système TCP) |
| Catch `Exception` global | Tu masques des bugs Python (clés manquantes dans `data[...]`, etc.) |
| Ne pas appeler `raise_for_status()` | Tu prends un `data = response.json()` sur une réponse 500 — `KeyError` plus loin |
| Hardcoder `http://localhost:8000` côté UI Docker | `Connection refused` — il faut `http://api-nlp:8000` (nom de service) |
| Réinstancier `httpx.Client()` à chaque appel | Surcoût connexion TCP, ~30-100 ms par appel inutilement |
| `response.text` au lieu de `response.json()` quand l'API renvoie JSON | Tu manipules une str, pas un dict — erreurs `[..]` plus loin |

Symptôme → cause probable :

| Symptôme | Cause probable |
|---|---|
| `httpx.ConnectError` immédiat | Service cible pas démarré OU mauvaise URL (`localhost` au lieu de nom de service docker) |
| Timeout systématique sous Docker | `start_period` du healthcheck trop court, l'API n'est pas prête au premier appel |
| `KeyError` sur `data["sentiment"]` | La réponse API n'a pas la forme attendue (regarde `response.text`), souvent une 422 ou 500 mal catchée |
| `httpx.UnsupportedProtocol` | URL malformée (`api-nlp:8000` sans `http://`) |
| `SSL: WRONG_VERSION_NUMBER` | Tu fais du `https://` vers un service qui sert du `http://` |
| `'response' is not defined` dans `except` | Tu utilises `response` dans un `except` qui peut être levé avant l'assignation. Utilise `exc.response` (sur `HTTPStatusError`) ou capture en amont. |

## Pour aller plus loin

- Doc officielle httpx : <https://www.python-httpx.org/>
- Quick start : <https://www.python-httpx.org/quickstart/>
- Exceptions reference : <https://www.python-httpx.org/exceptions/>
- Async client (pour M5/M7 quand on parlera de scaling) :
  <https://www.python-httpx.org/async/>
- Comparaison `httpx` vs `requests` : <https://www.python-httpx.org/compatibility/>
- Tester un endpoint en CLI sans Postman : `curl -X POST http://localhost:8000/predict
  -H 'Content-Type: application/json' -d '{"texte":"..."}'`
- **Repo officiel httpx** (lecture des tests pour patterns avancés —
  retries, connection pooling, mocks) : <https://github.com/encode/httpx>
- **Tenacity** — décorateur de retry combinable avec `httpx` quand
  l'API cible est instable (utile dès qu'on parlera de résilience en
  M5/M6) : <https://tenacity.readthedocs.io/en/latest/>

## Vérification (checklist apprenant)

- [ ] Je sais que **tout appel HTTP réseau doit avoir un `timeout`** explicite
- [ ] Je connais la hiérarchie d'exceptions httpx (`HTTPError` → `RequestError` /
      `HTTPStatusError`) et je sais distinguer un timeout d'un 500
- [ ] J'utilise `raise_for_status()` pour transformer les 4xx/5xx en exception
- [ ] J'utilise `response.json()` quand l'API renvoie du JSON (pas
      `response.text` + `json.loads` manuel)
- [ ] Mon UI Streamlit affiche un **message d'erreur clair** pour chaque type
      d'échec API (timeout, HTTP error, réseau)
- [ ] J'ai pingé `/health` au démarrage pour valider que l'API est joignable
      (bonus)
