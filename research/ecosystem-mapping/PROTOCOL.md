# Protocole de cartographie écosystémique — pilote 0.1
Statut : proposition de recherche, à valider avant collecte complète. Le corpus v0.2.0 et le catalogue de production (2466 fiches) restent inchangés.

## Objectif et unité
Recenser les technologies susceptibles de servir directement ou indirectement l'enseignement/apprentissage de l'EPS au collège et au lycée au Maroc. Pas de quota final. Un enregistrement de source n'est pas une technologie unique : conserver les identifiants de plateforme, rapprocher les variantes uniquement sur preuves (éditeur, produit, site officiel). Un produit peut porter plusieurs catégories. Conserver les cas ambigus pour revue.

## Sources et collecte
- Rejouer/récupérer les archives précédentes (non disponibles dans cette session); documenter empreintes, versions et périmètres avant fusion.
- App Store: 16 familles, 5 expressions dans chacune des trois langues, 4 boutiques (MA/FR/US/GB); 240 expressions, 960 requêtes prévues pour la matrice complète. Le pilote exécute une expression par famille et langue, dans une boutique associée (48 requêtes). Limite pilote 50, complet 200 résultats; résultats limités/non exhaustifs. Au moins 3,5 s entre requêtes, erreurs distinctes des zéros, reprise par journal.
- F-Droid: index officiel, à intégrer au pilote multisource suivant; API Google Play Catalog soumise à éligibilité; Aptoide, GitHub et annuaires via interfaces autorisées. Pas de contournement, ni de collecte d'APK. Les logos ne sont pas téléchargés; droits d'affichage à vérifier. Les données brutes sont destinées à l'audit, pas à la republication sans examen des droits.
- Définir et pré-enregistrer le plan de saturation (rendement marginal par source/famille, requêtes complémentaires, plafonds et échecs signalés). Ne pas utiliser la popularité comme exclusion.
Sources : https://performance-partners.apple.com/search-api ; https://f-droid.org/en/docs/All_our_APIs/ ; https://developers.google.com/android-publisher/play-catalog ; https://www.prisma-statement.org/scoping (adaptation de transparence, pas une revue systématique).

## Criblage et évaluation
Conserver toutes les observations brutes, y compris jeux, social et genres généralistes. Criblage après normalisation : direct EPS / complémentaire avec scénario d'usage identifiable / non pertinent (motif) / incertain. Évaluer les risques scolaires indépendamment de la pertinence; pas de recommandation tant qu'une contrainte critique est inconnue. Ne pas déduire une efficacité pédagogique de la description éditeur. Vérifier source, disponibilité Maroc, âge, prix, appareils, langues, fonctionnement hors ligne, données et autorisations.
Référentiel: annexe E3 originale, 97 codes reproduits dans framework_10d97p.json. D1–D6 et D10: examiner l'applicabilité à l'outil/usage; D7–D9: portent largement sur processus/cadre/système; ne pas les noter mécaniquement pour chaque app. La portée exacte et les ancres doivent être validées paramètre par paramètre. Échelle originale 1–5; NR (non renseigné) et SO (sans objet) proposés séparément pour la nouvelle cartographie, non assimilés à 0 ou 3. Grille des 18 critères historique à conserver séparément, avec méthode et version; pas de prétendue équivalence automatique.
Avant extension : double criblage indépendant d'un échantillon stratifié incluant cas difficiles, mesurer accord et faux négatifs; arbitrage et révision du codebook. Prévoir échantillon indépendant de contrôle; seuils et taille à fixer avant l'analyse. Aucun filtre automatique par score avant cette validation.

## Pilote et résultats
Le script archive les réponses, journaux, empreintes SHA256, effectifs source, identifiants uniques Apple, champs manquants, chevauchements et plafonds. Aucun ajout au catalogue. Rapport d'exécution avec effectifs observés, pas d'estimation de l'univers. Les fonctions pédagogiques restent à vérifier. Ne pas fusionner les variantes intersources sans validation.
Après pilote : audit du vocabulaire, couverture, erreurs, droits, puis décision de lancement complet. L'extension écosystémique devra être évaluée séparément : couverture de besoins, redondance, faisabilité cumulée, sécurité, charge numérique et engagement moteur.
