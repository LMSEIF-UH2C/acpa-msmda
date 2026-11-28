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

## Fondements méthodologiques et matrice de conformité (ajout après pilote exploratoire)
Le pilote a été déclenché avant cet amendement; ne pas présenter ce texte comme préenregistré avant le pilote. Préenregistrer la version finale avant collecte définitive. La revue porte sur des produits numériques, pas uniquement des articles. La transposition des méthodes mHealth à l'EPS est une adaptation proposée, non une validation.
- Gasteiger et al. (2023), TECH, BMJ Open 13:e073283, https://doi.org/10.1136/bmjopen-2023-073283 : structurer la question, la recherche exploratoire, l'éligibilité, la recherche définitive, l'extraction, l'évaluation et la synthèse. TECH : utilisateurs cibles (enseignants/élèves), focus de l'évaluation, connectivité/interactions, domaine (santé dans l'original, EPS ici).
- Marshall et al. (2020), Apps With Maps, JMIR Mental Health 7:e16525, https://doi.org/10.2196/16525 : PASSR (annexe de l'article), adaptation de PRISMA et AMSTAR 2 aux recherches dans les boutiques. Utiliser comme guide de transparence et documenter les écarts; ne pas le présenter comme standard universel validé.
- Gasteiger et al. (2025), https://doi.org/10.1093/jamiaopen/ooae159 : revue de la qualité du reporting des revues d'applications, justification du futur CAPPRRI.
- Gasteiger et al. (2026), CAPPRRI, accepté/sous presse le 27 octobre 2026, https://research.manchester.ac.uk/en/publications/development-of-a-guideline-for-reporting-systematic-mobile-health/ ; https://equator-network.org/reporting-guidelines/under-development/consensus-for-app-review-reporting-items-capprri/ : le résumé institutionnel annonce 31 items et un diagramme. Grille complète non consultée; aucune revendication de conformité à CAPPRRI avant récupération et comparaison item par item.
- Martin et al., A Survey of App Store Analysis for Software Engineering, https://doi.org/10.1109/TSE.2016.2630689 : justifier l'ingénierie de collecte, les unités d'analyse, les métadonnées et les limites de couverture.
- Annexe E3 du doctorat : 10D/97P, référentiel disciplinaire original. Établir une table de correspondance paramètre/preuve/unité d'évaluation avant la cotation. L'extension écosystémique est une hypothèse à tester, distincte des résultats antérieurs.

| Bloc | Preuve ou livrable exigé avant exploitation |
|---|---|
| Question et périmètre TECH | Question explicite, utilisateurs, usages EPS directs et complémentaires, connectivité et contexte marocain |
| Accès et collecte | Registre des sources, conditions d'accès et de réutilisation, versions d'API, marchés, dates, paramètres, plafonds, erreurs et empreintes |
| Identification PASSR | Journal des recherches, effectifs par source, correspondances interplateformes prouvées, diagramme réconcilié |
| Criblage | Codebook, décisions direct/complémentaire/exclu/incertain, motifs, deux juges indépendants sur échantillon stratifié et contrôle des faux négatifs |
| Extraction et cotation | Version de l'outil, données factuelles, preuves par paramètre, NR/SO séparés, distinction entre fonctionnalités annoncées, testées et efficacité empirique |
| Synthèse | Effectifs réconciliés, couverture et biais, résultats par famille et niveau de preuve; pas de quota ni prétention d'exhaustivité |
| Reporting CAPPRRI | Récupérer la grille finale, construire correspondance item par item et justifier non-applicabilité avant publication |
| Écosystèmes | Règles de complémentarité, contraintes cumulées, test indépendant par scénarios et experts; ne pas attribuer une efficacité non évaluée |

Avant collecte massive : auditer les résultats du pilote, élargir progressivement les sources autorisées, valider le codebook et les 97 correspondances, fixer les seuils et le plan d'échantillonnage, archiver le protocole final daté. Aucune fusion de la PR dans main ni modification du catalogue publié à ce stade.
