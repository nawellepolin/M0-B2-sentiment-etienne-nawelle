# Hugging Face Transformers (CamemBERT) — Mini-cours

> Brief associé : M0-B2
> Durée de lecture : ~35 min
> Pré-requis : Python 3.11, notions FastAPI (M0-B1)

## Pourquoi cette techno ?

Pour faire du NLP en français en 2026, **personne** ne (ré)entraîne un
modèle depuis zéro pour des tâches courantes (sentiment, classification,
NER, traduction). On part d'un **modèle pré-entraîné** publié sur le
*Hugging Face Hub* — la place de marché de facto des modèles open
weights — et on l'utilise tel quel, ou on l'adapte (fine-tuning, mapping
de classes, prompt).

La librairie **`transformers`** de Hugging Face fournit l'abstraction
**`pipeline`** : 3 lignes pour charger un modèle, son tokenizer et lancer
une inférence. C'est le standard de l'industrie pour prototyper et
déployer du NLP rapide.

Alternatives :
- **spaCy** : excellent pour le NLP « classique » (NER, POS, parsing),
  moins adapté aux tâches text-classification dérivées de BERT.
- **Stanza** (Stanford) : focus académique, moins mainstream en prod.
- **API tierces** (OpenAI, Cohere, Mistral API) : zéro infra mais coût
  par requête + données qui sortent du SI. Hors scope ici.

Dans M0-B2, on consomme **`cmarkea/distilcamembert-base-sentiment`** : un
DistilCamemBERT (variante distillée + légère de CamemBERT) fine-tuné sur
le sentiment FR. Le modèle pèse ~270 Mo, l'inférence CPU est de l'ordre
de 50-200 ms par texte court.

## Concepts clés

- **Pipeline** : la classe haut-niveau `transformers.pipeline(task=...,
  model=...)` qui encapsule le tokenizer, le modèle et le post-processing
  pour une **tâche** (`text-classification`, `ner`, `summarization`, etc.).
- **Tokenizer** : il convertit le texte FR en tokens entiers compatibles
  avec le modèle. Pour CamemBERT, c'est un tokenizer **SentencePiece** —
  d'où les dépendances `sentencepiece` et `protobuf` indispensables, à
  ne pas oublier dans `requirements.txt`.
- **`top_k=None`** dans le pipeline : retourne **toutes les classes**
  avec leur probabilité (utile pour le mapping 5★ → 3 et la traçabilité).
  Par défaut, le pipeline ne renvoie que la classe top-1.
- **Cache HF** : la 1ʳᵉ exécution télécharge le modèle depuis le Hub
  vers `~/.cache/huggingface/` (ou la variable `HF_HOME`). Les runs
  suivants chargent depuis le cache. Dans M0-B2, on monte ce cache en
  volume Docker pour éviter de re-télécharger à chaque `up`.
- **Mapping de classes** : un modèle sur étagère a souvent un **format
  de sortie qui ne correspond pas au métier**. Le geste cœur du brief M0-B2
  est de mapper les labels natifs du modèle vers les classes utiles au
  client. Ici : 5★ → `négatif/neutre/positif`.

## ⚠️ Deux choses à savoir avant de coder

### 1. Le pipeline renvoie une **liste de listes**

Quand tu appelles `pipeline(text)` avec **un seul texte en entrée**, le
retour n'est pas une liste de scores, c'est une liste qui contient une
liste de scores. C'est-à-dire :

```python
result = pipeline("Personnel charmant, chambre impeccable !")
# result = [
#   [
#     {'label': '5 stars', 'score': 0.6},
#     {'label': '4 stars', 'score': 0.3},
#     ...
#   ]
# ]
result[0]      # ← la liste des 5 scores pour ton texte
result[0][0]   # ← le premier score (avec la plus haute proba)
```

Pourquoi cette enveloppe ? Parce que le pipeline accepte aussi des
**batches** (`pipeline([text1, text2, ...])`), et il renvoie alors une
liste de listes, un élément par texte. L'enveloppe est conservée même
quand tu envoies un seul texte. Mémorise `result[0]` — c'est le piège HF
débutant numéro 1.

### 2. Le premier appel est lent (« warmup »)

Le tout premier `pipeline(text)` après le chargement du modèle prend
**2 à 5 secondes** sur CPU. Les appels suivants tournent en **50 à
200 ms**. C'est dû à l'initialisation interne de PyTorch (allocations
mémoire, kernels CPU optimisés).

| Appel | Latence typique CPU |
|---|---|
| 1ᵉʳ après démarrage | 2-5 s (warmup) |
| Suivants | 50-200 ms |

→ Dans M0-B2, le `lifespan` charge le pipeline mais ne fait pas de
warmup explicite. Le 1ᵉʳ `/predict` peut donc paraître anormalement
lent — c'est attendu. En prod, on **précharge** avec un appel bidon au
démarrage (« warmup request »).

## Exemple minimal qui tourne

```python
# /tmp/test_camembert.py
from transformers import pipeline

# 1. Charger le pipeline (tokenizer + modèle + post-processing)
sentiment = pipeline(
    task="text-classification",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    top_k=None,                       # toutes les classes, pas seulement le top-1
)

# 2. Inférer sur un texte FR
text = "Personnel charmant, chambre impeccable, on reviendra !"
result = sentiment(text)
print(result)
# [[
#   {'label': '5 stars', 'score': 0.6},
#   {'label': '4 stars', 'score': 0.3},
#   {'label': '3 stars', 'score': 0.05},
#   {'label': '2 stars', 'score': 0.03},
#   {'label': '1 star',  'score': 0.02},
# ]]

# 3. Mapping 5★ → 3 classes métier
def map_stars_to_sentiment(label: str) -> str:
    stars = int(label.split()[0])
    if stars <= 2:
        return "négatif"
    if stars == 3:
        return "neutre"
    return "positif"

top_label = result[0][0]['label']       # le label avec la plus haute proba
print(map_stars_to_sentiment(top_label))  # 'positif'
```

Versions utilisées dans M0-B2 :
- `transformers==4.46.3`
- `torch==2.5.1` (CPU)
- `sentencepiece==0.2.0`
- `protobuf>=3.20,<5`

## Exercice guidé

Dans `services/api-nlp/app/inference.py` du squelette, complète
`predict_sentiment()` :

1. **Mesure le temps d'inférence** avec `time.perf_counter()` avant et
   après l'appel au pipeline.
2. **Appelle** le pipeline : `pipeline(text, top_k=None)`. Note bien :
   le résultat est une liste de listes — `result[0]` est la liste des
   classes pour ton (unique) input.
3. **Reconstruis** un `dict[str, float]` `scores_5_stars` à partir de
   `result[0]`.
4. **Trouve** le label argmax (celui avec la plus haute proba). Indice :
   `max(result[0], key=lambda x: x['score'])['label']`.
5. **Appelle** `map_stars_to_sentiment(top_label)` pour obtenir la classe
   métier.
6. **Retourne** un `SentimentOut(sentiment=..., scores_5_stars=...,
   model_name=model_name, latence_ms=...)`.

<details><summary>▶ Voir la solution complète (à dérouler seulement après avoir essayé)</summary>

```python
def predict_sentiment(pipeline, text: str, model_name: str) -> SentimentOut:
    start = time.perf_counter()
    raw = pipeline(text, top_k=None)
    latence_ms = (time.perf_counter() - start) * 1000

    scores_5_stars = {item["label"]: item["score"] for item in raw[0]}
    top_label = max(raw[0], key=lambda x: x["score"])["label"]
    sentiment = map_stars_to_sentiment(top_label)

    return SentimentOut(
        sentiment=sentiment,
        scores_5_stars=scores_5_stars,
        model_name=model_name,
        latence_ms=round(latence_ms, 2),
    )
```

</details>

**Justification du seuil de mapping** (attendu dans le README perso async) :
le choix `1-2→négatif / 3→neutre / 4-5→positif` est *un* choix possible.
On peut aussi élargir le neutre vers le négatif (`2-3→neutre`, dans ce
cas seul `1 star` reste négatif — plus de prudence avant de cataloguer
une review comme négative), ou inversement durcir le positif (`5 stars`
seul → positif). Le bon seuil dépend du métier client (combien de faux
négatifs acceptables, coût d'un faux positif, etc.). Documente le tien.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Oublier `sentencepiece` ou `protobuf` dans `requirements.txt` | `ImportError` au chargement du tokenizer CamemBERT |
| Ne pas mettre `top_k=None` | Le pipeline renvoie seulement le top-1, impossible de reconstruire les scores 5★ |
| Charger le pipeline à chaque requête `/predict` | Latence x10-20, mémoire qui explose. À charger une fois au `lifespan`. |
| Ignorer la variable `HF_HOME` dans Docker | Le modèle est re-téléchargé à chaque `up` (270 Mo perdus, build de cache inutile) |
| Mapper en dur sans justification | Le seuil de mapping est un **choix métier** — sans doc, impossible à maintenir |
| Utiliser `tblard/tf-allocine` comme fallback dans cette stack | ⚠️ Ce modèle est **TensorFlow-only**, incompatible avec notre stack `torch`. Cité ici comme contre-exemple. |

Symptôme → cause probable :

| Symptôme | Cause probable |
|---|---|
| `ModuleNotFoundError: No module named 'sentencepiece'` | Dep manquante dans `requirements.txt` |
| `Failed to import google.protobuf` | Dep manquante (`protobuf>=3.20,<5`) |
| Pipeline qui retourne `[{'label': 'LABEL_0', 'score': ...}]` | Modèle sans `id2label` dans sa config — vérifier la model card |
| Latence > 1 s par appel court | Le pipeline est re-instancié à chaque requête (pas chargé au lifespan) |
| Conteneur qui exit OOMKilled | RAM insuffisante allouée à Docker Desktop (< 4 Go), CamemBERT en a besoin de ~1 Go |
| `OSError: Can't load tokenizer` après changement de modèle | Cache HF corrompu, supprimer `./models/` et relancer `docker compose up --build` |

## Pour aller plus loin

- Doc officielle Transformers : <https://huggingface.co/docs/transformers/index>
- Model card du modèle utilisé : <https://huggingface.co/cmarkea/distilcamembert-base-sentiment>
- Pipeline API référence : <https://huggingface.co/docs/transformers/main_classes/pipelines>
- HF Course (gratuit, FR/EN) : <https://huggingface.co/learn/nlp-course>
- Livre : **Natural Language Processing with Transformers (2ᵉ éd.)**,
  L. Tunstall, L. von Werra, T. Wolf — chapitre 2 sur le pipeline
- Modèles alternatifs FR : `cmarkea/distilcamembert-base-nli`,
  `dangvantuan/sentence-camembert-base`

## Vérification (checklist apprenant)

- [ ] Je peux expliquer en 2 minutes ce qu'est un *pipeline* Hugging Face
      et à quoi il sert
- [ ] J'ai compris pourquoi `top_k=None` est important dans M0-B2 (besoin de
      toutes les classes, pas juste le top-1)
- [ ] Je sais que `sentencepiece` et `protobuf` sont indispensables pour
      CamemBERT (tokenizer SentencePiece)
- [ ] Je sais où est cachée la valeur du modèle téléchargé (`HF_HOME`,
      volume Docker `./models`)
- [ ] J'ai implémenté `map_stars_to_sentiment` ET `predict_sentiment` dans
      le squelette M0-B2, j'ai justifié mon seuil de mapping en commentaire
- [ ] Mon `/predict` retourne bien une classe `négatif/neutre/positif`,
      jamais une étoile brute