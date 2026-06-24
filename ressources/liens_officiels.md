# Liens officiels — M0-B2

Dernière vérification : 2026-05-13

## Documentation officielle

- **Docker Compose** : <https://docs.docker.com/compose/>
  - Sections recommandées : *Overview*, *Compose file reference*, *Networking*, *Healthchecks*
  - État : ✅ vérifié le 2026-05-13
- **Compose Specification** (référence) : <https://github.com/compose-spec/compose-spec/blob/main/spec.md>
  - État : ✅ vérifié le 2026-05-13
- **Hugging Face Transformers** : <https://huggingface.co/docs/transformers/index>
  - Sections recommandées : *Quick tour*, *Pipelines*, *Tokenizer*
  - État : ✅ vérifié le 2026-05-13
- **Streamlit** : <https://docs.streamlit.io>
  - Sections recommandées : *Get started*, *API reference*, *Layouts and containers*
  - État : ✅ vérifié le 2026-05-13
- **httpx** : <https://www.python-httpx.org/>
  - Sections recommandées : *Quickstart*, *Exceptions*, *Timeouts*
  - État : ✅ vérifié le 2026-05-13
- **FastAPI lifespan** : <https://fastapi.tiangolo.com/advanced/events/#lifespan>
  - État : ✅ vérifié le 2026-05-13
- **Pydantic v2** : <https://docs.pydantic.dev/latest/>
  - Sections recommandées : *Models*, *Validators*, *Fields*
  - État : ✅ vérifié le 2026-05-13

## Modèles Hugging Face utilisés

- **`cmarkea/distilcamembert-base-sentiment`** (modèle imposé) :
  <https://huggingface.co/cmarkea/distilcamembert-base-sentiment>
  - 68 M paramètres, 5 classes étoiles, FR natif
  - État : ✅ vérifié le 2026-05-13
- **`tblard/tf-allocine`** (alternative documentée, **non utilisée**) :
  <https://huggingface.co/tblard/tf-allocine>
  - ⚠️ TensorFlow-only, binaire POSITIVE/NEGATIVE, incompatible avec
    notre stack PyTorch — cité en contre-exemple dans le mini-cours 02
  - État : ✅ vérifié le 2026-05-13

## Tutoriels et articles

- **HF NLP Course** (gratuit, EN/FR) : <https://huggingface.co/learn/nlp-course>
  - Chapitre 1-2 pour comprendre le pipeline
  - État : ✅ vérifié le 2026-05-13
- **httpx — Async Quickstart** : <https://www.python-httpx.org/quickstart/>
  - État : ✅ vérifié le 2026-05-13
- **Streamlit Cheatsheet** : <https://docs.streamlit.io/library/cheatsheet>
  - État : ✅ vérifié le 2026-05-13

## Vidéos

- **Docker Compose en 12 min** (FreeCodeCamp) :
  <https://www.youtube.com/watch?v=HG6yIjZapSA>
  - État : ✅ vérifié le 2026-05-13
- **Streamlit in 30 minutes** (Streamlit official) :
  <https://www.youtube.com/watch?v=R2nr1uZ8ffc>
  - État : ✅ vérifié le 2026-05-13

## Repositories de référence

- **Awesome Compose** (exemples multi-services) :
  <https://github.com/docker/awesome-compose>
  - Exemple `fastapi/` particulièrement pertinent pour M0-B2
  - État : ✅ vérifié le 2026-05-13
- **Streamlit gallery** (apps démos) :
  <https://streamlit.io/gallery>
  - État : ✅ vérifié le 2026-05-13
- **Examples Streamlit officiels** :
  <https://github.com/streamlit/streamlit/tree/master/examples>
  - État : ✅ vérifié le 2026-05-13