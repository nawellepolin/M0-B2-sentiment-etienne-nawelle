# M0-B2 — Pack ressources

> Brief M0-B2 « Déployer une IA NLP packagée — sentiment FR chez Aubergine
> Hôtels ». Sentiment FR avec CamemBERT, orchestration `docker compose`,
> UI Streamlit, mapping 5★ → 3 classes.

## Pour qui ?

Apprenants Dev-id Parcours 2 (IT pros) — semaine 2 de la formation.

- **Sync mercredi** : binôme tiré au sort, 3h45 + 15 min tour de table
- **Async jeudi/vendredi matin** : individuel (fork du repo binôme)

## Ce que tu trouves ici

| Fichier | Quand le mobiliser | Durée de lecture |
|---|---|---|
| [`01_DockerCompose_essentiel.md`](./01_DockerCompose_essentiel.md) | Tâches 1, 2 (mise en route + analyse de la stack), Tâche 5 (côté compose : volume `./logs`) | ~30 min |
| [`02_HuggingFace_Transformers_essentiel.md`](./02_HuggingFace_Transformers_essentiel.md) | Tâche 3 (implémenter `/predict` + mapping 5★→3) | ~35 min |
| [`03_Streamlit_essentiel.md`](./03_Streamlit_essentiel.md) | Tâche 4 (UI utilisateur) | ~25 min |
| [`04_API_Integration_essentiel.md`](./04_API_Integration_essentiel.md) | Tâche 4 (côté UI : httpx + gestion erreurs) | ~25 min |
| [`liens_officiels.md`](./liens_officiels.md) | Recherche méthodique à tout moment | — |

> 💡 La **Tâche 5 (Logging Loguru)** mobilise deux ressources
> complémentaires : le mini-cours `03_Loguru_essentiel.md` de M0-B1 (lien
> ci-dessous) pour la configuration Loguru côté code Python, **et** le
> mini-cours `01_DockerCompose` ci-dessus pour le volume `./logs` qui
> persiste les logs entre redémarrages. Tâche 6 (tests pytest) idem avec
> le mini-cours pytest de M0-B1.

## Ce que tu ne trouves pas ici (mais qui te servira)

**Réutilisation depuis M0-B1** — pas de duplication :

- **Loguru** (journalisation) :
  [`ia-dev-id-parcours-m0-b1 · ressources/03_Loguru_essentiel.md`](https://github.com/Formation-SIMPLON-IA/ia-dev-id-parcours-m0-b1/blob/main/ressources/03_Loguru_essentiel.md)
- **Pytest API** (tests fonctionnels) :
  [`ia-dev-id-parcours-m0-b1 · ressources/04_Pytest_API_essentiel.md`](https://github.com/Formation-SIMPLON-IA/ia-dev-id-parcours-m0-b1/blob/main/ressources/04_Pytest_API_essentiel.md)
- **Docker (Dockerfile)** :
  [`ia-dev-id-parcours-m0-b1 · ressources/02_Docker_essentiel.md`](https://github.com/Formation-SIMPLON-IA/ia-dev-id-parcours-m0-b1/blob/main/ressources/02_Docker_essentiel.md)

**Ressources legacy OPCO ATLAS** (compléments optionnels) : disponibles
**à la demande sur Discord** auprès de la formatrice. Pour M0-B2, la doc
Streamlit ATLAS (~1620 mots, plus détaillée que notre mini-cours)
complète utilement `03_Streamlit_essentiel.md`.

## Ordre suggéré de consultation

1. **Avant la séance sync** (10 min) : lire la « Situation professionnelle »
   du brief sur Simplonline + ce README + parcourir
   `01_DockerCompose_essentiel.md` (au moins la section « Pourquoi »).
2. **Pendant la sync mercredi** : ouvrir chaque mini-cours dans l'ordre des
   tâches (`01` pour démarrage stack, `02` pour `/predict`, `03` + `04`
   pour l'UI).
3. **En async** : revenir sur les sections « Pièges fréquents » et
   « Symptôme → cause probable » des mini-cours quand tu débugges un
   problème en autonomie.

## Squelette de code

Le squelette de code, ce sont les fichiers à la **racine de ce repo** (créé
via « Use this template » — cf. [`README.md`](../README.md) racine). La stack
tourne dès le clone via `docker compose up --build` (3-5 min de build au
premier démarrage). 1 test pytest passe d'office, `/predict` renvoie 501
(stub à compléter).
