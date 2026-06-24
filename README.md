# M0-B2 — Squelette repo (sentiment FR · stack `docker compose`)

> **Repo template GitHub.** Clique sur **« Use this template »** en haut à
> droite de cette page → **Create a new repository** → nomme-le
> `M0-B2-sentiment-<prénom>` sur **ton** compte GitHub personnel.
> C'est ce nouveau repo que vous clonerez pour travailler.

Brief **M0-B2 « Déployer une IA NLP packagée — sentiment FR chez Aubergine
Hôtels »** — mercredi semaine 2.
**Sync** : binôme tiré au sort, 4 h (3h45 + 15 min tour de table).
**Async** : individuel, 4 h (fork du repo binôme).
L'énoncé complet est publié sur **Simplonline**.

---

## 🚀 Démarrage (3 commandes)

```bash
# 0. Clone ton repo perso fraîchement créé
git clone git@github.com:<ton-user>/M0-B2-sentiment-<prenom>.git
cd M0-B2-sentiment-<prenom>

# 1. Configurer l'environnement
cp .env.example .env

# 2. Construire et lancer la stack
docker compose up --build

# 3. Vérifier
curl http://localhost:8000/health        # API NLP
open  http://localhost:8501              # UI Streamlit
```

À l'arrêt : `Ctrl+C` puis `docker compose down` (les volumes `models/` et
`logs/` sont conservés — le modèle HF n'est pas re-téléchargé au prochain `up`).

> ⏱️ Le **1ᵉʳ démarrage** prend 3-5 min de build + 1-3 min de download du
> modèle DistilCamemBERT (~270 Mo). Les démarrages suivants sont < 30 s grâce
> au cache volume `models/`.

---

## 🧠 Modèle utilisé

**`cmarkea/distilcamembert-base-sentiment`** — DistilCamemBERT FR, 68 M
paramètres, ~270 Mo.

⚠️ Le modèle sort **5 étoiles** (`'1 star'` … `'5 stars'`). Le métier
(Aubergine Hôtels) veut **3 classes** (`négatif/neutre/positif`).

→ Tu dois implémenter le **mapping 5★ → 3 classes** dans
`services/api-nlp/app/inference.py`. **C'est le geste cœur de ce brief**
(adaptation d'un service au format métier — C6 N2).

---

## 📁 Structure du repo

```
M0-B2-sentiment-<prenom>/
├── docker-compose.yml             ← 2 services + healthcheck api-nlp
├── .env.example
├── services/
│   ├── api-nlp/                   ← FastAPI + transformers
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py            ← routes (lifespan + /health + /info + /predict)
│   │   │   ├── schemas.py         ← Pydantic ReviewIn / SentimentOut
│   │   │   └── inference.py       ← TON CODE + mapping 5→3
│   │   └── tests/
│   │       └── test_health.py     ← 1 test pytest qui passe
│   └── ui-streamlit/              ← UI utilisateur
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app.py                 ← UI à compléter (brancher l'appel HTTP)
├── data/
│   └── sample_reviews.csv         ← 30 reviews FR fictives (Aubergine Hôtels)
├── postman/
│   └── M0-B2_collection.json      ← à compléter (≥ 5 requêtes)
├── ressources/                    ← 📚 mini-cours d'appui (lecture juste-à-temps)
│   ├── 01_DockerCompose_essentiel.md
│   ├── 02_HuggingFace_Transformers_essentiel.md
│   ├── 03_Streamlit_essentiel.md
│   ├── 04_API_Integration_essentiel.md
│   ├── liens_officiels.md
│   └── README.md
├── .gitignore
└── README.md (ce fichier — à compléter avec ta doc + schéma Mermaid)
```

---

## ✏️ Endpoints fournis

| Endpoint | Statut au clone | Ce que tu dois faire |
|---|---|---|
| `GET /health` | ✅ fonctionnel | rien |
| `GET /info` | ✅ fonctionnel | rien |
| `POST /predict` | ❌ 501 Not Implemented | implémenter (avec mapping 5→3) |

L'UI Streamlit est lancée mais affiche **« API non branchée »** tant que tu
n'as pas branché l'appel HTTP dans `services/ui-streamlit/app.py`.

---

## 🧭 Démarche attendue

### Sync — mercredi 9h-13h (binôme)

| # | Étape | Mini-cours | Durée |
|---|---|---|---|
| 1 | Tirage binômes + démarrage stack | (ce README) | 30 min |
| 2 | Analyse du squelette + model card HF | — | 30 min |
| 3 | Implémenter `/predict` + **mapping 5★ → 3 classes** | [`02_HuggingFace_Transformers`](./ressources/02_HuggingFace_Transformers_essentiel.md) | 1 h 15 |
| 🍴 | **Switch des rôles binôme** (API ↔ UI) | — | 10 min |
| 4 | Brancher l'UI Streamlit à l'API | [`03_Streamlit`](./ressources/03_Streamlit_essentiel.md) + [`04_API_Integration`](./ressources/04_API_Integration_essentiel.md) | 50 min |
| 5 | Logging Loguru | mini-cours M0-B1 réutilisé | 30 min |
| 6 | Tests pytest `/predict` | mini-cours M0-B1 réutilisé | 35 min |
| 7 | **Tour de table** d'avancement + critères modèle | plénière | 15 min |

### Async — jeudi/vendredi (individuel, fork du repo binôme)

| # | Étape | Priorité | Durée |
|---|---|---|---|
| A | README perso + **schéma Mermaid** d'architecture | 🔴 critique | 1 h |
| B | **Analyse de ≥ 3 reviews mal classées** + hypothèse explicative | 🔴 critique | 1 h |
| C | Compléter la collection Postman (≥ 5 requêtes, cas limites) | 🟠 important | 45 min |
| D | Justification du seuil de mapping retenu (½ page) | 🟠 important | 15 min |
| E | **Bonus** : healthcheck custom avec retry | 🟢 libre | 30 min |
| F | **Bonus** : endpoint `/predict/batch` | 🟢 libre | 30 min |
| G | **Bonus** : pourquoi CamemBERT plutôt qu'un LLM (½ page) | 🟢 libre | 30 min |

Cf. [`./ressources/README.md`](./ressources/README.md) pour le détail.

---

## 🎯 Ce qui compte vraiment

1. **Une stack qui tourne** avec healthcheck `healthy`. `docker compose up
   --build` démarre sans erreur.
2. **Le mapping 5★ → 3 classes implémenté et justifié** (le geste C6 N2).
3. **L'UI Streamlit branchée à l'API** via le réseau docker interne
   (nom de service `http://api-nlp:8000`, **pas** `localhost`).
4. **≥ 3 tests pytest qui passent** depuis le conteneur.
5. **Un README perso avec schéma Mermaid** lisible.
6. **L'analyse des reviews mal classées** : ≥ 3 cas avec hypothèse typée
   (ironie / négation / comparatif / mixte / ambivalence).

---

## 🤝 Modalité binôme sync — règles du jeu

- **Tirage au sort** par la formatrice mercredi 9h. Pas de libre choix.
- **Une seule branche commune** (`main`).
- **Commits identifiés** : `Co-authored-by:` quand vous codez ensemble.
- **Switch obligatoire à mi-séance** (~10h45) : API ↔ UI, brief mutuel de
  10 min avant.
- **Personne ne termine le sync sans avoir touché aux deux côtés.**

En async : **fork/clone** du repo binôme dans `M0-B2-sentiment-<prenom>`, tu
travailles **seul·e**. Livrable critique = README perso + analyse reviews.

---

## ✅ Tests & environnement

```bash
docker compose exec api-nlp pytest -v      # tests dans le conteneur API
docker compose ps                          # api-nlp doit être (healthy)
```

| Variable (`.env`) | Défaut | Usage |
|---|---|---|
| `MODEL_NAME_HF` | `cmarkea/distilcamembert-base-sentiment` | Modèle HF à charger |
| `MAX_TEXT_LENGTH` | `2000` | Validation Pydantic (longueur max texte) |

---

## 🆘 Bloqué·e ?

| Symptôme | À tenter |
|---|---|
| `docker compose up` bloqué sur `pulling/building` | 1ᵉʳ build = 3-5 min + 1-3 min download modèle, patiente |
| `/predict` renvoie toujours 501 | `inference.py` pas encore complété — normal |
| `/predict` renvoie `"1 star"` au lieu de `"négatif"` | Mapping 5→3 pas implémenté |
| L'UI affiche « API non branchée » | Compléter `app.py` dans `services/ui-streamlit/` |
| `Connection refused` depuis l'UI | URL = `http://api-nlp:8000` (nom de service), pas `localhost` |
| `ModuleNotFoundError` | Rebuild : `docker compose build --no-cache api-nlp` |
| Service `unhealthy` après 2 min | `docker compose logs api-nlp` (réseau / mémoire / chargement modèle) |

Logs en temps réel : `docker compose logs -f api-nlp`. **Demande en direct
mercredi 9h-13h** — Discord ouvert, on est ensemble. RDV vendredi sinon.