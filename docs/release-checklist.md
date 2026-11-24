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
- [ ] Vérification manuelle PDF/CSV/JSON et des messages d'erreur ; confirmer les limites de conservation.
- [x] Revue documentaire de confidentialité et de déploiement : voir privacy-deployment.md ; ne constitue pas un audit juridique.
- [ ] Confirmer les contrôles en situation réelle et les conditions d’hébergement avant usage institutionnel.
- [ ] CI verte sur le commit candidat ; identifier la version et publier les notes de version, sans modifier rétroactivement le DOI archivé.

## Après la première version

Bibliothèque de situations plus complète, validation scientifique indépendante, transcription vérifiée des orientations pédagogiques, extension hors ligne et vidéo, IA générative et communauté. Le compagnon terrain et le module vidéo restent expérimentaux jusqu'à leurs essais et leur déploiement. Les objectifs SUS et réussite des tâches nécessitent une évaluation avec des utilisateurs, non une estimation.

Référence accessibilité : https://www.w3.org/TR/WCAG22/
