# Checklist de stabilisation

Une fusion ou un succès CI ne constitue pas une validation scientifique, ergonomique ou réglementaire.

## Avant une version candidate

- [x] 15 socles fonctionnels fusionnés ; périmètres expérimentaux identifiés.
- [x] PR 38 : tests automatiques réussis ; APS précise et sauvegarde journal v4 intégrées.
- [x] PR 39 : parcours automatisés avec journal rempli, contexte partagé et trois langues.
- [x] PR 41 : accueil mobile compact ; deux workflows réussis.
- [x] PR 42 : Amiri locale et licence OFL, autoévaluation descriptive, sauvegarde en langage courant ; deux workflows réussis.
- [x] PR 43 : continuité Technothèque, Évaluer et Scénario ; deux workflows réussis.
- [x] PR 44 : capacité annuelle et restauration, deux workflows réussis.
- [x] PR 45 : correctif CSS des cartes iPhone, deux workflows réussis ; confirmation visuelle restante.
- [ ] Essai réel sur ordinateur, iPhone et Android : navigation, lisibilité, focus, contraste, défilement, RTL, clavier, taille des cibles ; aucune certification WCAG à ce stade.
- [ ] Essai manuel création cycle, créneaux, génération, projet de classe, studio, export, restauration et bilan.
- [ ] Vérification manuelle PDF/XLSX, sauvegarde-restauration XLSX et messages d'erreur ; CSV et JSON uniquement dans les usages scientifiques avancés concernés ; confirmer les limites de conservation.
- [x] Revue documentaire de confidentialité et de déploiement : voir privacy-deployment.md ; ne constitue pas un audit juridique.
- [ ] Confirmer les contrôles en situation réelle et les conditions d’hébergement avant usage institutionnel.
- [ ] CI verte sur le commit candidat ; identifier la version et publier les notes de version, sans modifier rétroactivement le DOI archivé.

## Gel technique et préparation de v0.2.0

- [x] PR #50, #51 et #52 fusionnées ; notices scientifiques et parcours test-retest contrôlés.
- [x] Deux workflows post-fusion réussis sur `48f8d915` : 188 tests chacun.
- [ ] Deux workflows réussis sur la révision documentaire finale.
- [ ] Recette réelle et confirmation du déploiement ; concordance des variantes bibliographiques.
- [ ] Publication du tag v0.2.0 après réception, sans revendication de production institutionnelle.
- [ ] Valorisation et archivage distincts après finalisation.

## Clôture v0.2.0 (25 novembre 2026)

- [x] PR #68 réconciliée avec `main` (après #70 à #74) ; traductions fusionnées sans perte ; moteur scientifique inchangé.
- [x] Contributions des PR #59 et #67 reprises ; #59, #67 et #69 fermées sans fusion, branches conservées.
- [x] Révision `96ad264` : 262 tests (3.12 et 3.14), démonstration web, R 29/29, navigation mobile : réussis.
- [x] Recette navigateur : 60/60 visites (10 pages, FR/AR/EN, ordinateur et iPhone simulé) ; banque visuelle et barre d'onglets contrôlées.
- [x] Documents de livraison, CHANGELOG, CITATION.cff (0.2.0), NOTICE et version du paquet actualisés.
- [ ] Recette physique iPhone : `docs/recette-iphone-v0.2.0.md`.
- [ ] Fusion de #68 puis de la PR de préparation ; CI verte sur le commit final de `main`.
- [ ] Accord final du porteur, puis tag, release GitHub et dépôt Zenodo : `docs/publication-v0.2.0.md`.

## Après la première version

Bibliothèque de situations plus complète, validation scientifique indépendante, transcription vérifiée des orientations pédagogiques, extension hors ligne et vidéo, IA générative et communauté. Le compagnon terrain et le module vidéo restent expérimentaux jusqu'à leurs essais et leur déploiement. Les objectifs SUS et réussite des tâches nécessitent une évaluation avec des utilisateurs, non une estimation.

Référence accessibilité : https://www.w3.org/TR/WCAG22/
