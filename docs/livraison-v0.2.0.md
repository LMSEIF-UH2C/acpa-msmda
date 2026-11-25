# Dossier de livraison ACPA/MSMDA v0.2.0

Index des preuves, validations, limites et conditions de publication. Statut : clôture documentaire réalisée ; publication en attente de la recette physique iPhone et de l'accord explicite du porteur du projet. Aucun tag, release ni DOI n'est attribué à ce stade.

## 1. Identification

| Élément | Valeur |
|---|---|
| Version | 0.2.0 (`CITATION.cff`, `src/acpa_msmda/__init__.py`, CHANGELOG) |
| Dépôt | https://github.com/LMSEIF-UH2C/acpa-msmda |
| Démonstration publique | https://acpa-msmda.streamlit.app/ |
| Dernière révision de code vérifiée | `d265de3` (fusion de la PR #75) ; la PR de clôture documentaire ne modifie aucun code exécuté par l'application |
| Commit à étiqueter | commit de `main` qui portera la date de publication effective, après CI réussie |
| Version archivée précédente | v0.1.1, DOI 10.5281/zenodo.23244629 (moteur heuristique distinct ; DOI à ne pas réutiliser) |

## 2. Validations

| Contrôle | Résultat | Preuve |
|---|---|---|
| Tests automatisés, Python 3.12 et 3.14 | 262 tests sur `d265de3` (264 avec les deux tests de concordance de l'en-tête du catalogue ajoutés à la clôture) | runs 45654736522 et 45653913441 ; CI de la PR de clôture |
| Démonstration web publique | 262 tests sur `d265de3` | run 45654736492 |
| Comparaison indépendante avec R 4.5.2 | 29/29 métriques | run 45653913393 |
| Navigation mobile | 30/30 configurations (320 à 430 px, Chromium et WebKit, FR/AR/EN) ; dictée simulée 2/2 | run 45653913411 |
| Parcours de recette | 17/17 | `scripts/check_release_flows.py` |
| Balayage navigateur | 60/60 visites (10 pages, 3 langues, ordinateur et iPhone simulé) | `docs/validation/recette-cloture-v0.2.0-2026-11-25/` |
| Sauvegardes Excel réenregistrées par un tableur tiers puis restaurées | identiques (évaluation formative, journal, projets de cycle) | audit final indépendant |
| Banque visuelle | 14 illustrations conformes à leurs empreintes ; 18 pictogrammes | `assets/visual-bank/manifest.json` |
| Recette physique iPhone | **à réaliser** | `docs/recette-iphone-v0.2.0.md` |

Les nombres de tests des jalons successifs (188, 205, 211, 262) ne s'additionnent pas.

## 3. Dossiers de preuves

- Registre historique des validations, échecs et incidents : `docs/validation/README.md`, `docs/validation/workflow-history-2026-11-24.csv`.
- Pistes de validation antérieures et réconciliation du corpus : `docs/validation/ANTERIOR_VALIDATION_LEADS.md`.
- Recettes : `docs/validation/recette-modules-2026-11-24/`, `restitution-lab-2026-11-24/`, `rec-y002-mobile-navigation/`, `banque-visuelle-2026-11-25/`, `recette-cloture-v0.2.0-2026-11-25/`.
- Statut scientifique, formule de score et cartographie : `docs/statut-scientifique-v0.2.0.md`.
- Références des instruments : `docs/LAB_REFERENCE_AUDIT.md`, `docs/scientific-validation.md`.

Les échecs, corrections et arbitrages successifs sont conservés tels quels ; ils font partie de la traçabilité.

## 4. Licences, crédits et propriété intellectuelle

- Code : licence MIT (`LICENSE`).
- Illustrations du Laboratoire : générées par IA, retenues par le porteur du projet, non normatives ; CC BY 4.0 dans la mesure des droits détenus (`assets/visual-bank/LICENCE-ILLUSTRATIONS.md`).
- Pictogrammes OpenMoji : CC BY-SA 4.0, fichiers non modifiés.
- Polices : Amiri et IBM Plex Sans Arabic sous SIL OFL ; DejaVu sous sa licence (`assets/fonts/`).
- Demande de brevet OMPIC n° 74877, 23 avril 2026, non accordée ; aucune licence de brevet n'est concédée (`NOTICE`).

## 5. Contributions

- Porteur du projet (Youness Moudettir) : conception scientifique et pédagogique, choix des instruments et des illustrations, arbitrages, validation de chaque fusion.
- Encadrement scientifique et co-inventeurs : Saïd Lotfi et Siham Ouhrir.
- Assistants d'IA (ChatGPT et Claude) : propositions de code, documentation, audits et recettes, soumises par pull request, relues et fusionnées par le porteur. Les commits sont signés au nom du dépôt ou du porteur ; l'attribution d'une contribution ne se déduit pas du seul compte GitHub (`docs/validation/README.md`).
- Ressources tierces : OpenMoji, Amiri, IBM Plex Sans Arabic, DejaVu.

## 6. PR closes sans fusion

| PR | Motif | Reprise dans `main` |
|---|---|---|
| #59, #67 | banque visuelle préparatoire | reprises dans la PR #68 (handgrip exclu volontairement) |
| #69 | correctif de la barre d'onglets | remplacée par la PR #70 |
| #11, #12, #13, #15 | interface, contexte partagé, séries de mesures, avis des enseignants | têtes ancêtres de `main` : contributions intégrées |
| #9 | icônes et navigation de l'accueil | dépassée par #11, #70 et #71 |
| #2 | registre de cinq outils réels | remplacé par le répertoire de 2 466 fiches ; LINCE PLUS et les fonctions relevées pour OBS Studio non repris (piste après v0.2.0) |

Toutes les branches sont conservées.

## 7. Limites connues, non bloquantes

Voir `docs/release-v0.2.0.md`, section « Limites connues ». En résumé :
- aucune validation empirique de v0.2.0 ;
- notes du répertoire majoritairement estimées ;
- données temporaires et service en ligne seulement ;
- dictée testée en simulation tant que la recette iPhone n'est pas faite ;
- réserves sur certaines illustrations ;
- libellés internes de Streamlit et badge Community Cloud ;
- `use_container_width` à remplacer avant une montée de version ;
- circulaire 2358/25 non inspectée ;
- compagnons hors ligne et vidéo expérimentaux.

Plan de levée : lots C (correctif v0.2.1) et D (travaux après la soutenance) du plan d'action du 25 novembre 2026.

## 8. Conditions restantes avant publication

1. Recette physique iPhone sans anomalie bloquante.
2. Informations bibliographiques à confirmer par le porteur :
   - ORCID des trois auteurs ;
   - rattachement de Siham Ouhrir au LMSEIF ;
   - graphie « Saïd » ou « Said » ;
   - ordre des auteurs.
3. Le jour de la publication : `date-released` dans `CITATION.cff`, statut publié dans le README, les notes de version et le CHANGELOG ; CI réussie sur ce commit.
4. Accord explicite du porteur, puis tag `v0.2.0`, release GitHub et dépôt Zenodo selon `docs/publication-v0.2.0.md`, avec vérification du rattachement à l'enregistrement v0.1.1.
