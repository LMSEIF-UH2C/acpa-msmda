# ACPA/MSMDA v0.2.0 — Préparation de publication

Statut : gel technique candidat, publication et recette réelle restantes. Aucun nouveau DOI ni tag stable attribué à ce stade.

## Révision de référence

Le commit `48f8d915cc3f63969433fa87944cab5e65b492e0` a passé 188 tests sur chacun des deux workflows GitHub Actions après fusion de la PR #52 : [Tests ACPA MSMDA](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45407016207) et [Public web demo](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45407016185). La révision documentaire suivante doit également être validée avant publication.

## Périmètre

- Évaluation, recherche contextualisée, technothèque et Studio ; continuité du contexte.
- Espace EPS : ateliers, terrain, évaluation formative, cahier journalier et sauvegardes portables.
- Laboratoire : 19 instruments, références ou sources apparentées, notices FR/AR/EN et quatre entrées méthodologiques (ICC, Bland–Altman, SEM/MDC95, d_z).
- PR #50 : progressivité des usages ; PR #51 : documentation scientifique ; PR #52 : tests supplémentaires de rendu et de test-retest.

## Limites et conditions de publication

La stabilité logicielle ne signifie pas validation empirique des protocoles, efficacité pédagogique, conformité réglementaire ou aptitude à une production institutionnelle. Les références apparentées et les variantes des instruments restent à confirmer. Les séries sont temporaires ; utiliser des exemples fictifs sur le service public et exporter avant fermeture. Les compagnons hors ligne et vidéo restent expérimentaux.

Avant publication : contrôler le rendu réel sur ordinateur, iPhone et Android, le RTL, les exports et la restauration ; confirmer la révision déployée ; valider les deux workflows sur la révision finale ; créer la release GitHub v0.2.0 seulement après réception. Ne pas réutiliser le DOI de v0.1.1. Le rapport de valorisation et Zenodo sont reportés.

## Traçabilité du développement

Le rapport ultérieur distinguera les tests distincts, les exécutions cumulées de tests et les workflows réussis ou échoués. Les échecs seront analysés par cause, correction et validation ultérieure, sans assimiler chaque workflow échoué à une anomalie distincte. Sources : [Pull requests](https://github.com/LMSEIF-UH2C/acpa-msmda/pulls?q=is%3Apr), [Actions](https://github.com/LMSEIF-UH2C/acpa-msmda/actions).

Voir [checklist](release-checklist.md), [guide](teacher-guide.md) et [confidentialité](privacy-deployment.md).
