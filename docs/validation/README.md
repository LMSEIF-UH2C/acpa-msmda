# Registre historique des validations ACPA/MSMDA

Instantané du 24 novembre 2026, établi avant les commits documentaires de cette branche.

## Historique CI

[workflow-history-2026-11-24.csv](workflow-history-2026-11-24.csv) : 494 identifiants uniques de workflows retrouvés via cinq pages de l'API GitHub Actions (494 annoncés initialement). Période 2026-11-21T20:37:58Z à 2026-11-24T20:13:33Z, UTC.

| Workflow | Résultats par statut |
|---|---|
| Public web demo | failure: 76; success: 194 |
| Tests ACPA MSMDA | failure: 52; success: 166 |
| Independent R validation | success: 6 |

Total par conclusion : {"failure":128,"success":366}.

Les lignes représentent des identifiants d'exécution de workflow, non des cas de test, ni des anomalies uniques. run_attempt est le numéro de tentative visible; les anciennes tentatives et les journaux expirés ne sont pas récupérés par cet export. Aucun cumul de cas exécutés n'est inféré à partir du nombre de workflows. Les journaux détaillés, les essais locaux et les validations empiriques doctorales constituent des sources distinctes. Ne pas attribuer automatiquement les commits à Claude ou ChatGPT sur la base du compte GitHub.

## Jalons vérifiés

| Révision | Preuve | Résultat |
|---|---|---|
| 48f8d915 | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45407016207 | 188 tests |
| 0ae44bc0 | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45451392880 | 205 tests |
| a34912dd | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45452647206 | 205 tests |
| 087145ed | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45470077434 | 29/29 comparaisons R 4.5.2 |
| a55cb572 | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45476404977 | 211 tests avant fusion |
| 90ef0334 | https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45478536654 | 211 tests après fusion, 41,392 s |

## Incidents documentés (sélection, non exhaustive)

| PR | Incident | Correction / preuve |
|---|---|---|
| 52 | Formatage traduit hors contexte de langue en AppTest | Libellés prétraduits; suite à 188 tests validée |
| 57 | Bouton de téléchargement supplémentaire dans le parcours ordinaire | Espace étude facultatif; tests ensuite réussis |
| 59 | Fichiers JPEG non transférés | PR ouverte, tests bloquants; intervention Claude nécessaire |
| 61 | DOI EMEP classé dans les liens complémentaires | 0dcc739b; trois workflows réussis |
| 62 | Risque de surcharge graphique et de rerun au téléchargement | Limites de présentation et on_click=ignore; 211 tests après fusion |

## Maintenance

Avant chaque livraison, exporter un nouvel instantané paginé, dédupliquer par run ID, conserver les tentatives séparément si récupérables, archiver les preuves de chaque échec significatif et de sa correction, les jeux synthétiques et les résultats indépendants. Pour le rapport final, compter séparément les identifiants de cas de test, les exécutions de suites, les workflows et les comparaisons R. Les essais manuels de Youness et Claude doivent être datés et associés au commit, appareil, scénario, résultat et capture si disponible.

Sources : https://github.com/LMSEIF-UH2C/acpa-msmda/actions et https://docs.github.com/en/rest/actions/workflow-runs

## Recettes de la phase 2

- [Recette des modules hors Laboratoire, 24 novembre 2026](recette-modules-2026-11-24/README.md)
