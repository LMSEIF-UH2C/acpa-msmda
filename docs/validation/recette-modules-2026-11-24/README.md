# Recette des modules hors Laboratoire EPS : 24 novembre 2026

Synthèse reproductible de la recette interactive de la phase 2. Elle porte sur tous les modules sauf la partie
graphique du Laboratoire EPS : la compatibilité Altair et Python 3.14, le secours graphique et les tests associés
sont traités dans une branche dédiée. Rôles : porteur du projet (essais sur appareils réels, décisions),
assistant de développement (recette simulée, corrections, preuves).

## Version testée

| Élément | Valeur |
|---|---|
| Base | `main` à 9a46943 (PR #63 incluse) ; code identique à 90ef033, les commits suivants ne touchent que la documentation |
| Corrections | branche `recette/v0.2.0-modules`, commit indiqué dans la PR de recette |
| Python | 3.12.3, environnement neuf installé depuis `requirements.txt` (versions exactes) |
| Streamlit | 1.47.1 ; Altair 5.5.0 ; SciPy 1.18.1 |
| Navigateur | Chromium sans interface (Playwright), ordinateur 1366 × 900 et iPhone 13 simulé (390 × 844) |

## Tests réalisés

| # | Test | Méthode | Résultat |
|---|---|---|---|
| R1 | Suite automatisée, compilation, contrôle de mutation, moteur publié | Mêmes commandes que la CI | 211 tests réussis avant correction ; 215 après (4 tests ajoutés) |
| R2 | Ouverture des 10 pages × 3 langues × 2 appareils (60 ouvertures) | `scripts/sweep.py` | 60/60 : aucune exception, aucune erreur JavaScript, aucun débordement horizontal ; sens de lecture `rtl` en arabe, `ltr` sinon |
| R3 | Relecture visuelle des 30 écrans iPhone en arabe et en anglais | Planches `captures/iphone_toutes_pages_*.jpg` | 2 anomalies relevées (A1, A2) |
| R4 | Continuité du contexte : effectif modifié dans Scénarisation, relu dans Organiser les ateliers après navigation par la barre d'onglets | `scripts/f_flows.py` | Réussi en FR, AR et EN sur iPhone, et en FR sur ordinateur |
| R5 | Exports : organisation PDF et CSV, scénario PDF et CSV, rapport PDF de la Technothèque | `scripts/f_flows.py` | 20 fichiers produits, en-têtes `%PDF` valides, CSV UTF-8 avec BOM ; PDF arabe de droite à gauche (`captures/exports_pdf_ar_en.jpg`) |
| R6 | Technothèque : recherche, barre d'état, « Nouvelle recherche » | `scripts/f_flows.py` | 2 466 applications examinées, 89 retenues, analyse en 63 à 74 ms ; la demande est bien vidée |
| R7 | Cahier journalier : import d'une sauvegarde synthétique (2 cycles, 2 créneaux, 1 interruption, 22 séances), réexport, CSV | `scripts/f_journal.py`, `resultats/journal_synthetique.json` | Aller-retour identique sur les 6 rubriques ; CSV de 22 séances ; en AR et en FR |
| R8 | Évaluer votre contexte, Évaluation formative, Cahier journalier (saisie), 6 outils du mode terrain, Espace EPS en 3 langues | `scripts/apptest_flows.py` | 17/17 étapes réussies (`resultats/parcours_apptest.json`) |
| R9 | Mode terrain : minuteur en marche en arabe et en anglais | `scripts/f_field.py` | Après correction A1 : libellés traduits pendant le décompte (`captures/flow_field_ar.jpg`) |
| R10 | Laboratoire : import longitudinal de 2 880 observations synthétiques (lecture seule, sans modification du module) | `scripts/f_lab.py`, `scripts/generer_lab_synthetique.py` | Import accepté sous Python 3.12, en local et sur l'application déployée ; aucune exception sur la vue par défaut. Les graphiques ne sont pas évalués ici |
| R12 | Intégration continue sur la PR de recette, fusionnée virtuellement avec `main` à f7044f4 (PR #64 incluse) | GitHub Actions | Tests sous Python 3.12 et 3.14 réussis ; démonstration publique réussie ; validation indépendante avec R réussie : https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45505666486 |
| R11 | Application déployée | Playwright sur https://acpa-msmda.streamlit.app | Écran de choix de la langue affiché ; import Lab identique au local |

## Anomalies et corrections

| Id | Constat | Gravité | Correction | Preuve |
|---|---|---|---|---|
| A1 | Mode terrain en arabe et en anglais : pendant le décompte, « Temps restant », « Démarrer », « Pause » et « Réinitialiser » repassent en français. Cause : le fragment relancé chaque seconde (`st.fragment(run_every=1)`) ne repasse pas par la configuration de la langue. | Moyenne | `i18n.current()` relit la langue de la session quand le contexte d'exécution n'en a pas, ce qui couvre tout fragment présent ou futur | `tests/test_i18n_fragments.py`, `captures/flow_field_ar.jpg` |
| A2 | « Évaluer votre contexte » : le champ de choix multiple affiche « Choose options », texte par défaut de Streamlit, dans les trois langues | Faible | Texte indicatif traduit : « Choisir dans la liste », « اختر من القائمة », « Choose from the list » | Vérifié en AR et EN après redémarrage |
| A3 | Deux-points à la française (« libellé : valeur ») en arabe et en anglais : Scénarisation (5 cas), Évaluation formative, Cahier journalier, Évaluer votre contexte, PDF de l'évaluation formative | Faible | Séparateur selon la langue (`i18n.colon()`) | Suite complète réussie |

## Points relevés non corrigés

| Id | Constat | Raison |
|---|---|---|
| N1 | Le déploiement tourne sous Python 3.14 (erreur Altair rapportée sur iPhone), alors que `DEPLOYMENT.md` demande Python 3.12 | Compatibilité 3.14 apportée par la PR #64 (fusionnée pendant la recette) ; `DEPLOYMENT.md` reste à harmoniser avec la version réellement retenue |
| N2 | Textes intégrés de Streamlit non traduisibles en 1.47 : zone de dépôt (« Drag and drop file here », « Browse files », « Limit… per file ») et calendrier des champs de date | Limite de la bibliothèque, pas d'anomalie de l'application |
| N3 | Laboratoire : un multiple choix sans texte indicatif traduit et un deux-points à la française | Fichier `pages/2_Performance_Lab.py` en cours de correction dans une autre branche : à reprendre ensuite |
| N4 | `src/acpa_msmda/__init__.py` indique 0.1.0 alors que `CITATION.cff` indique 0.2.0-rc.1 | Numéro de version à fixer au moment de la livraison, sur décision du porteur du projet |
| N5 | Badge Streamlit en bas à droite qui recouvre une partie de la barre d'onglets sur l'application déployée | Reporté au lot 6, après la v0.2.0 |

## Reste à faire

- Essais sur appareils réels par le porteur du projet (iPhone et Android) : chaque essai daté, avec le commit, l'appareil, le parcours, le résultat et une capture.
- Validation indépendante avec R à refaire sur le commit final de livraison.
- Recette graphique du Laboratoire après fusion de la branche de compatibilité.
- Illustrations prioritaires (PR #59) à réception de l'archive.

## Reproduire

```bash
python -m pip install -r requirements.txt playwright
python -m unittest discover -s tests -p 'test_*.py'
streamlit run app.py --server.headless true --server.port 8599 &
python docs/validation/recette-modules-2026-11-24/scripts/sweep.py
```

Les scripts écrivent leurs résultats et captures dans un dossier de travail : adapter la variable `OUT` en tête
de chaque script.
