# Référentiel interne UX — ACPA/MSMDA

> **Document de cadrage interne uniquement.** Les références Nielsen, Bastien–Scapin, ISO et WCAG servent à concevoir, examiner et améliorer le produit. Elles ne constituent ni un label, ni une certification, ni une promesse de conformité, et ne doivent pas être utilisées comme arguments marketing ou affichées dans l'interface. L'expérience utilisateur doit démontrer la qualité du produit par les tâches accomplies, la clarté et la fluidité.

## Objectif
Faire d'ACPA/MSMDA un exemple de clarté, de contrôle utilisateur et d'utilisabilité en situation réelle d'EPS. Ce document guide les arbitrages, sans revendiquer une conformité ou validation obtenue.

## Références
- Nielsen Norman Group, 10 heuristics: https://www.nngroup.com/articles/ten-usability-heuristics/
- Bastien & Scapin (1993), Ergonomic Criteria for the Evaluation of Human-Computer Interfaces, INRIA Research Report 156: https://hal.inria.fr/inria-00070012
- ISO 9241-11:2018, Usability: https://www.iso.org/standard/63500.html
- ISO 9241-210:2019, Human-centred design: https://www.iso.org/standard/77520.html
- WCAG 2.2: https://www.w3.org/TR/WCAG22/

## Principes applicables dès maintenant
1. **Visibilité** : confirmer l'action, afficher clairement l'état de recherche, les limites et l'absence de résultats (Nielsen).
2. **Langage métier** : employer les termes des enseignants d'EPS ; éviter le jargon de recherche, les compteurs de catalogue et les sigles inexpliqués (Nielsen ; compatibilité Scapin).
3. **Contrôle explicite** : déclencher les recherches coûteuses sur action de l'utilisateur ; permettre de revenir, corriger et effacer (Scapin).
4. **Charge de travail** : présenter d'abord les quatre tâches principales ; limiter les informations secondaires et les longues tables (Scapin).
5. **Cohérence** : mêmes libellés, composants, navigation et feedback entre les modules (Nielsen ; Scapin).
6. **Prévention des erreurs** : contrôler durées, formats, champs requis et restrictions de données personnelles avant export (Nielsen).
7. **Adaptabilité** : écran mobile, grandes cibles tactiles, contraste et lisibilité au soleil, connexions faibles (Scapin ; WCAG).
8. **Aide contextuelle** : expliquer pourquoi un outil est suggéré, ses limites et les alternatives sans technologie (Nielsen).
9. **Accessibilité** : parcours clavier, labels explicites, ordre de focus, contrastes, alternatives textuelles et test de lecteur d'écran (WCAG 2.2).
10. **Transparence** : distinguer fiches renseignées, vérifiées et non évaluées sans encombrer l'accueil.

## Critères d'acceptation de la V2.1
- Depuis l'accueil, un enseignant atteint chacune des quatre tâches en une action.
- Une recherche vide affiche un message utile et n'exécute pas de recommandation.
- Une recherche sans résultat offre une alternative et l'accès au catalogue.
- Sur largeur de 375 px, les actions principales sont lisibles, sans débordement horizontal.
- Le catalogue ne force pas le défilement d'un tableau large et présente des fiches ouvrables.
- Chaque outil proposé explique au moins un motif de correspondance et ses incertitudes.
- Les erreurs de durée du scénario sont signalées avant export.
- Aucun champ de l'accueil ne demande des données nominatives d'élèves.
- Les parcours essentiels sont vérifiés au clavier et avec un lecteur d'écran.

## Protocole d'évaluation utilisateur à conduire
Échantillon diversifié d'enseignants d'EPS (niveaux, expérience, appareils, connectivité), sans présumer d'un effectif universel.
Tâches : trouver une technologie pour une séance sans internet ; comparer deux outils ; créer et exporter un scénario ; trouver un test dans Performance Lab.
Mesures : taux de réussite par tâche, temps, erreurs, demandes d'aide, satisfaction et verbalisations ; questionnaire SUS ou UMUX-Lite selon le protocole choisi ; relevé des incidents par gravité et par critère Nielsen/Scapin.
Ne pas présenter un score SUS, une conformité ISO ou une efficacité démontrée sans collecte et analyse effectives.
