# Changelog

Format inspiré de Keep a Changelog. Les numéros renvoient aux pull requests du dépôt. Une fusion ou une CI verte n'est pas une validation scientifique.

## [0.2.0] : en préparation

Révision consolidée vérifiée : `96ad264` (262 tests sous Python 3.12 et 3.14 ; R 4.5.2 : 29/29). Date de publication fixée lors du tag.

### Laboratoire EPS

- #50 : identification du laboratoire et progressivité des usages.
- #51 : références et informations scientifiques des instruments.
- #52 : informations trilingues et parcours test-retest.
- #54 : repères institutionnels et références complémentaires.
- #55 : sept nouveaux instruments de terrain référencés.
- #56 : bibliothèque documentaire et navigation progressive.
- #57 : données longitudinales codées et import CSV.
- #58 : analyses scientifiques courantes et mesures répétées.
- #60 : comparaison indépendante avec R (29/29 métriques), workflow dédié.
- #61 : audit documentaire des 32 instruments.
- #62 : stabilité des graphiques et des exports.
- #66 : restitution des analyses en trois niveaux (Comprendre, Analyser, Investiguer).
- #68 : repères visuels facultatifs : 14 illustrations générées par IA (dont 6 retouchées pour retirer des logos commerciaux) et 18 tests associés à des pictogrammes OpenMoji ; licences, crédits, empreintes SHA-256 et légendes FR/AR/EN ; nuance de chronométrage du sprint 30 m. Reprend les contributions utiles des PR #59 et #67, fermées sans fusion.

### Espace enseignant

- #73 : sauvegardes et exports en classeurs Excel restaurables (évaluation formative, cahier journalier, projets de cycle) ; refus des formules et des fichiers de plus de 10 Mo ; JSON conservé pour les usages techniques.
- #74 : dictée arabe sous Safari : transfert du texte vers la recherche, délai de secours, transcription multiligne RTL.

### Interface et compatibilité

- #64 : compatibilité Python 3.14 ; Streamlit 1.52.0 épinglé.
- #65 : recette des modules et corrections des anomalies constatées.
- #70 : centrage de la barre d'onglets mobile (remplace la PR #69, fermée sans fusion).
- #71 : charte marocaine et accueil.
- #72 : contour continu du bandeau d'accueil.

### Documentation et traçabilité

- #53 : gel technique et documentation de publication.
- #63 : registre historique des validations et dossier de livraison.
- Recette de clôture : `docs/validation/recette-cloture-v0.2.0-2026-11-25/` ; recette physique iPhone : `docs/recette-iphone-v0.2.0.md`.
- #75 : préparation de la publication, notes de version, métadonnées.
- Clôture documentaire : statut scientifique des composantes et adaptation de la formule de score (`docs/statut-scientifique-v0.2.0.md`) ; chiffres de cartographie harmonisés (45 676, 40 759, 2 466) ; auteurs et affiliations dans `CITATION.cff` ; `SECURITY.md` actualisé ; en-tête descriptif du catalogue recalculé à partir des fiches, sans modifier les fiches, avec un test de concordance ; dossier de livraison `docs/livraison-v0.2.0.md`.

### Limites connues

Voir `docs/release-v0.2.0.md`, section « Limites connues, non bloquantes ».

## [0.2.0-rc.1] : 24 novembre 2026

Version candidate, tag `v0.2.0-rc.1` (`2da291a`). Voir `docs/release-v0.2.0-rc.1.md`.

## [0.1.1] : 8 octobre 2026

Métadonnées de citation et documentation d'archivage du moteur heuristique. DOI : 10.5281/zenodo.23244629.

## [0.1.0] : 8 octobre 2026

Première publication du moteur heuristique avec catalogue synthétique.
