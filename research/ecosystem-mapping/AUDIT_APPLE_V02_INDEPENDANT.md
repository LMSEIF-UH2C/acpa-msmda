# Audit indépendant des archives Apple V0.2 — 28 novembre 2026

Phase 1 du [plan directeur](PLAN_FINALISATION.md). Audit hors ligne, sans requête supplémentaire aux boutiques. Archives téléchargées puis vérifiées dans le runtime indépendant du collecteur GitHub.

## Provenance et intégrité
| Archive | Run | Artefact | Fichiers | SHA-256 du ZIP |
|---|---|---|---:|---|
| Pilote initial | [46087551165](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46087551165) | 15239399393 | 98 | 7ae8e6d9b0bff727a2bfd322b30fb0f66d3aa0b8ae2ecda4cf82c764c7c50a4d |
| Extension V0.2 | [46128443244](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46128443244) | 15256204849 | 482 | 98657812ca3201aba2a0d9ad392d828db1600bef2ab32b387565e227339ba471 |

CRC ZIP vérifiés, aucun nom de fichier en double, correspondance bijective plans/journaux, URLs et paramètres exacts du plan, empreintes SHA-256 conformes pour 48 réponses brutes et 240 fichiers factuels, comptages cohérents, aucun fichier inattendu. Les empreintes des réponses API brutes V0.2 ne peuvent pas être recalculées, car ces réponses n'ont pas été conservées. Aucun contrôle d'authenticité indépendant du fournisseur ni de validité pédagogique. Toutes les 240 requêtes sont journalisées comme réussies au premier essai, 38 résultats vides, 0 plafonnée, 2 observations sans prix, aucun trackId manquant. Premier/dernier horodatage V0.2 09:01:03–09:19:11 UTC; ne pas assimiler cette durée à une comparaison de rapidité contrôlée. Diagramme historique DOCX : SHA-256 536dcc8640d4e77f45b60f2c5b505a4c932ca284e0f441fb9d7f766cb73fa00d, recalculé et conforme à la valeur du rapport maître.

## Effectifs réconciliés
48 requêtes initiales: 1 563 observations, 1 435 IDs. 240 requêtes V0.2: 5 424 observations, 2 362 IDs. Intersection 88, nouveaux vs premier pilote 2 274, union 3 709; 6 987 observations dans les deux phases. Tous les totaux du rapport V0.2 par terme, famille et cellule langue/marché ont été recalculés et concordent exactement. +158,5 % d'identifiants par rapport au premier pilote, non au corpus historique Apple de 23 194 IDs.

| Famille | Requêtes | Observations | IDs | Supplémentaires vs premier pilote | Exclusifs à cette famille dans V0.2 |
|---|---:|---:|---:|---:|---:|
| Communication | 48 | 1160 | 595 | 569 | 454 |
| Continuité | 72 | 1272 | 672 | 622 | 573 |
| Organisation | 48 | 1131 | 569 | 543 | 417 |
| Recherche/données | 72 | 1861 | 810 | 793 | 716 |

| Langue | Requêtes | Observations | IDs | Supplémentaires vs pilote | Exclusifs V0.2 | Vides |
|---|---:|---:|---:|---:|---:|---:|
| AR | 80 | 560 | 213 | 202 | 176 | 28 |
| EN | 80 | 2862 | 1354 | 1278 | 1213 | 0 |
| FR | 80 | 2002 | 958 | 945 | 816 | 10 |

| Marché | Requêtes | Observations | IDs | Supplémentaires vs pilote | Exclusifs V0.2 | Vides |
|---|---:|---:|---:|---:|---:|---:|
| FR | 60 | 791 | 701 | 674 | 105 | 14 |
| GB | 60 | 1776 | 1277 | 1224 | 396 | 9 |
| MA | 60 | 949 | 815 | 785 | 150 | 10 |
| US | 60 | 1908 | 1420 | 1351 | 446 | 5 |

Ensembles non disjoints; les exclusivités sont calculées dans la seule V0.2, pas par rapport à l'historique. Les 38 zéros sont des réponses API valides, pas des échecs. Les résultats descriptifs ne mesurent pas l'offre exhaustive ni un effet causal de la langue ou du marché.

## Redondance et analyse de sensibilité
Sur les 240 requêtes V0.2, 96 sans gain marginal dans l'ordre du plan conditionnellement au premier pilote (dont 38 vides), 121 sans aucun ID nouveau exclusif à cette requête relativement au premier pilote et aux autres requêtes V0.2; perte maximale si omission d'une requête = 25 IDs nouveaux. 28 680 paires possibles, 27 977 à union non vide (703 paires vide/vide exclues), 1 777 intersections non vides, Jaccard maximal 1. Pas d'exclusion automatique.
500 permutations, graine 20261128, couverture des 2 274 IDs supplémentaires observés conditionnellement aux 1 435 IDs du premier pilote. Ordre des 240 requêtes permuté, ensemble initial A fixe; dénominateur = |B\\A|. À chaque rang k, calcul de la médiane et des quantiles empiriques 5/95% des proportions, et du gain marginal médian au rang k. Quantiles interpolés linéairement; pas d'IC. 
| Rang k | Couverture médiane % | Q05–Q95 % | Gain marginal médian |
|---:|---:|---:|---:|
|60|42,370|36,539–49,079|7|
|120|69,371|63,760–74,894|4|
|180|87,731|83,773–91,163|2|
|216|95,646|93,621–97,628|1|
|240|100|100–100|0|

Sur union des 288 requêtes (sans corpus initial fixé), couverture médiane de l'union observée 3 709 IDs : 37,422 % à 72, 63,656 % à 144, 83,715 % à 216, 93,799 % à 259, 100 % à 288; gains médians aux mêmes rangs 13, 6, 3, 3, 3. Contrairement au premier pilote (gain final médian 29), redondance accrue dans cette extension ciblée. À 216/240, il reste environ 4,35% des 2 274 nouveaux IDs observés non retrouvés en médiane (environ 99); ce n'est pas une estimation de produits pertinents non trouvés. Le dernier gain médian nul ne démontre pas saturation du marché, ne justifie pas d'arrêt global; examiner les familles et les usages rares et tester des blocs de contrôle indépendants. Pas de seuil d'arrêt définitif.

## Décision et suite
Audit technique des archives Apple achevé; aucun appel réseau supplémentaire, aucune modification du catalogue. Les fichiers d'archive expirables doivent être conservés dans un espace autorisé. Comparaison avec les 45 676 enregistrements historiques reste bloquée par l'absence des listes historiques complètes. Ne pas sommer les IDs de source ou les dépôts comme des produits uniques. Prochaine étape : formaliser schéma produit/variante/observation/preuve, règles d'identité et jeu de tests sur cas ambigus; poursuivre récupération historique en parallèle, puis calibrer les juges. 
