# Recette de clôture v0.2.0 (25 novembre 2026)

Révision contrôlée : `96ad264`, branche `lab/visual-integration` (PR #68 réconciliée avec `main` à `1c0c249`, soit après les PR #70 à #74). Gel fonctionnel maintenu : aucune fonctionnalité ajoutée pendant la clôture.

## 1. Réconciliation de la PR #68 avec main

- Fusion de `origin/main` (merge, sans réécriture d'historique). Un seul conflit : `data/translations.json`.
- Résolution par fusion à trois voies clé par clé (base, PR #68, main) : 1 208 clés, union exacte, aucune valeur divergente.
- `pages/2_Performance_Lab.py` fusionné automatiquement ; seul écart avec main : six lignes de la banque visuelle (affichage du repère après la saisie et crédits dans « Statut scientifique et sources »).
- Sept fichiers hors ressources et preuves diffèrent de main : `NOTICE`, `data/translations.json`, `docs/validation/README.md`, `pages/2_Performance_Lab.py`, `src/acpa_msmda/visual_bank.py`, `tests/test_lab_illustrations.py`, `tools/i18n_strings.py`.
- Adaptation unique à Streamlit 1.52.0 : `st.image(..., width="stretch")` dans `visual_bank.py`, à la place du paramètre `use_container_width` déprécié.

## 2. Intégrité du moteur scientifique

Entre `84f107f` (fusion de la PR #66, révision où la restitution du laboratoire a été validée) et `96ad264`, aucun fichier du moteur ni des données scientifiques n'a changé (`scoring.py`, `lab_statistics.py`, `lab_results.py`, `reliability.py`, `measurements.py`, `longitudinal.py`, `context_engine.py`, catalogues). Seul `data/translations.json` a reçu 108 lignes de libellés. Comparaison indépendante avec R : 29/29 métriques conformes sur `96ad264`.

## 3. Résultats automatisés sur 96ad264

| Contrôle | Résultat | Source |
|---|---|---|
| Tests ACPA MSMDA, Python 3.12 | 262 tests, OK | run 45650091299 |
| Tests ACPA MSMDA, Python 3.14 | 262 tests, OK | run 45650091299 |
| Public web demo | 262 tests, OK | run 45650091292 |
| Independent R validation | 29/29 | run 45650091155 |
| Mobile navigation (REC-Y002 et dictée vocale simulée) | succès | run 45650091062 |
| Suite locale (Python 3.12.3, Streamlit 1.52.0 épinglé) | 262 tests, OK | environnement de recette |
| Chaînes manquantes FR/AR/EN (`tools/i18n_strings.py --missing`) | aucune | environnement de recette |
| `compileall`, contrôle de mutation | OK | environnement de recette |

Les 262 tests sont le nombre de tests distincts de la révision ; les exécutions des différents workflows ne s'additionnent pas.

Couverture ciblée par la suite : exports et restaurations Excel (évaluation formative complète, historique seul, journal, journal vide, projets de cycle, refus des formules, refus d'un mauvais format, rapport) ; sauvegardes du journal (aller-retour complet, version antérieure, version incompatible, spécialité) ; 5 tests d'export PDF ; 16 tests de restitution du laboratoire à trois niveaux ; banque visuelle (14 illustrations, 18 pictogrammes, empreintes SHA-256, légendes trilingues, nuance de chronométrage du sprint).

## 4. Recette navigateur (Chromium, gabarit iPhone 13 et ordinateur)

| Contrôle | Résultat | Fichier |
|---|---|---|
| Balayage 10 pages × 3 langues × 2 gabarits | 60/60 sans exception, alerte d'erreur, débordement, fuite de français ni erreur JavaScript | `resultats/balayage_pages.json` |
| Banque visuelle : 6 cas représentatifs et sprint 30 m en FR/AR/EN | images chargées, légendes RTL en arabe, aucun hôte externe | `resultats/banque_visuelle.json`, `resultats/legende_sprint.json` |
| Barre d'onglets mobile | de 10 à 380 px sur 390 px en FR/AR/EN | `scripts/mesure_tabbar.py` |
| Parcours AppTest | 16/17 ; le 17e attend encore des libellés « CSV » remplacés par « Excel » à la PR #73 (attente obsolète, non une régression) | `resultats/parcours_apptest.json` |

Ces contrôles simulent un iPhone dans Chromium. Ils ne remplacent ni Safari iOS ni un micro réel : voir `docs/recette-iphone-v0.2.0.md`.

## 5. Branches redondantes

- PR #67 : sa tête est un ancêtre de #68 ; fermée avec note, branche conservée.
- PR #59 : 7 des 8 illustrations prioritaires, ses critères de test et l'avertissement trilingue sont repris dans #68 ; l'illustration du handgrip est volontairement exclue ; `docs/LAB_ILLUSTRATIONS.md` est remplacé par le manifeste. Fermée avec note, branche conservée.
- PR #69 : remplacée par la PR #70. Fermée avec note, branche conservée.

## 6. Réserves non bloquantes

- Souplesse assise : l'élève est chaussé ; la légende le décrit. Aucune version sans chaussures n'a été reçue au 25 novembre 2026 (dossier Drive de livraison vérifié).
- Sprint 30 m : image conservée ; la légende précise la nuance de chronométrage (FR/AR/EN).
- Ressources Wikimedia : traitées séparément, non intégrées.
- Paramètre `use_container_width` encore présent dans du code antérieur (`app.py`, Espace Enseignant, Studio, `lab_results.py`) ; avertissement de dépréciation sans effet sous la version épinglée 1.52.0, à corriger avant toute montée de version de Streamlit.
