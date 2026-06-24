# Dataset `sample_reviews.csv` — vérité terrain validée

## Distribution finale

| Classe | Nombre |
|---|---|
| négatif | 11 |
| neutre | 8 |
| positif | 11 |
| **Total** | **30** |

## Décision éditoriale

On conserve volontairement ce déséquilibre 11/8/11. Deux raisons :

- **Réalisme métier** — dans la vraie vie, les datasets de reviews sont
  presque toujours déséquilibrés (les clients écrivent quand ils sont
  contents ou mécontents, rarement quand leur expérience est moyenne).
  Présenter un dataset 10/10/10 idéal donnerait une image fausse de ce
  qu'on rencontre en prod.
- **Difficulté intrinsèque du neutre** — le neutre textuel est plus
  difficile à juger qu'un positif ou un négatif franc. Forcer un
  rebalancing arithmétique nécessiterait de tordre des labels existants
  (ce qu'on refuse) ou d'ajouter des reviews neutres artificielles (ce
  qui appauvrit le dataset).

## Exploitation pédagogique

Ce déséquilibre est explicitement matière à enseignement dans le
**livrable async d'analyse des reviews mal classées**. L'apprenant peut
formuler l'hypothèse que la sous-représentation du neutre + son
ambiguïté intrinsèque expliquent une partie des erreurs du modèle.

## Statut

Vérité terrain **validée par Marianne le 2026-05-13**. Les labels actuels
sont définitifs, les pièges existants (ironie, négations, comparatifs
temporels, ambivalence, mixtes) sont validés et à préserver.

## Schéma du CSV

| Colonne | Type | Description |
|---|---|---|
| `id` | int | Identifiant 1-30 |
| `hotel` | str | Établissement fictif (préfixé *Aubergine*) |
| `texte` | str | Review FR (50-300 caractères) |
| `note_client` | int | Note 1-5 (contextuelle, **non utilisée** par le modèle) |
| `sentiment_attendu` | str | Vérité terrain en 3 classes (`négatif`/`neutre`/`positif`) |

Encodage UTF-8, séparateur `,`, header présent.

## Garde-fous

- Aucun nom d'employé réel.
- Aucun établissement réel : tous fictifs (Aubergine Bordeaux, Aubergine
  La Rochelle, etc.).
- Pas de donnée personnelle identifiable (RGPD-safe).