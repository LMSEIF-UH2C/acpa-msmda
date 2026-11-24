# Synthèse historique — 21–24 novembre 2026

Source : rapport « Rapport de synthèse et de suivi — ACPA/MSMDA » transmis intégralement par le porteur du projet le 24 novembre. Conversations indiquées : https://chatgpt.com/share/6b060608-2528-83ea-b275-ef9e06ffc3d9 et https://chatgpt.com/share/6b060680-ba88-83ea-9d24-89200c4e623b. Leur ouverture a échoué lors de cette transcription. Les observations et déclarations ci-dessous sont attribuées au rapport; aucune réexécution ni vérification des archives originales n'est revendiquée.

## Cartographie Apple
118 mots-clés anglais, 16 catégories EPS, 3 boutiques US/FR/GB, 354 requêtes via iTunes Search API entity=software, limite 200 sans pagination, intervalle 3,2 s, jusqu'à quatre essais. Collecte du 21 novembre vers 23h55 au 22 novembre 00h33 (début estimé). 23 194 trackId uniques après filtre initial des genres; nombre brut et rangs non journalisés. 12 392 dans une boutique, 5 636 dans deux, 5 166 dans trois. 285 noms identiques correspondent à 806 identifiants distincts. 7 643 sans avis. Archive déclarée collecte_catalogue_2026-11-22.tar.gz, préfixe SHA-256 dee36d18; empreinte complète non disponible ici.

| Genre | N |
|---|---:|
| Health & Fitness | 7693 |
| Sports | 5297 |
| Education | 2975 |
| Utilities | 2161 |
| Productivity | 1743 |
| Photo & Video | 1344 |
| Lifestyle | 688 |
| Navigation | 648 |
| Medical | 315 |
| Reference | 202 |
| Graphics & Design | 128 |

## Criblage et sélection
| Étape | Restantes | Écartées |
|---|---:|---:|
| Après filtre initial | 23194 | inconnu |
| Au moins 100 avis | 4976 | 18218 |
| Description obtenue | 4913 | 63 |
| Genres retenus | 4620 | 293 |
| Hors 17+ | 4254 | 366 |
| Termes exclus / grands réseaux | 4136 | 118 |
| Pertinence EPS | 2412 | 1724 |
| Classement, plafonds, dédoublonnage | 900 | 1512 |

Catalogue initial 204; prospection 1199 noms, 240 rapprochements exacts avec >=20 avis, 162 ajouts; recherche 100 noms, 16 confirmations sans ajout; sites officiels 173 proposés de mémoire, 113 acceptés initialement, 102 règle stricte, 77 ajoutés. Premier assemblage 1380 corrigé à 1343 = 204+900+162+77. Nouvelles fiches initialement OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW, masquées et non suggérées. Sélection par terme dans nom ou trois dans description, pertinence x log(avis), plafonds. 1964/2485 (79%) des résultats spécifiques EPS écartés par seuil 100 avis; biais contre outils spécialisés. Faux positifs et catégories erronées. Cartographie exploratoire structurée, pas revue systématique PRISMA.

## Android
Collecte massive ChatGPT non réalisée; 35 références exploratoires annoncées. Collecte Android distincte et rapprochement interplateforme confiés à Claude. 2466 fiches candidates PR16 annoncées; effectifs Android et rapprochement à réconcilier avec les sources primaires.

## Criblage assisté par IA
1876 lignes: 818 UTILE, 1058 NON UTILE. Correspondance exacte ID et ordre rapportée. Utiles: apprentissage sportif 411, planification 225, chronométrage 86, mesure performance 64, groupes/ateliers 17, analyse vidéo 13, évaluation 2. Non utiles: aucun usage EPS direct 904, régime/perte de poids 125, médical 21, réseau généraliste 4, jeu vidéo 4. Correction de règles: inclure exercice même orienté minceur; inclure cartes/GPS/boussoles/orientation. 207 lignes réévaluées, bilan non réconcilié. Pas de journal individuel ni validation humaine indépendante; gratuité et lecture approfondie non attestées. Ne pas assimiler criblage à validation scientifique.

## Jalons historiques
PR9 icônes à fermer après reprise; PR10 stabilisation CSV/dépendances, PR11 interface, PR12 contexte, PR13 mesures, PR14 catalogue 1343: CI réussie selon Claude. PR16 candidate 2466 fiches, 12 documentées fonctionnellement, 65 tests annoncés, non fusionnée et pending lors de l'inspection historique. Main 24 tests rapportés, branche interface 58, PR16 65. Suites potentiellement imbriquées, non additionnables. Voir [20 contrôles historiques](historical-controls-T01-T20.csv).

## UX, responsabilités et limites
Capture iPhone historique: accès réussi mais anciens emojis, grandes surfaces, sidebar peu apparente, bouton rouge, branding Streamlit et éléments flottants. Ne pas assimiler à la version actuelle ni certifier la branche candidate. Claude: collecte Apple/Android, refonte et correctifs; ChatGPT: criblage, audit partiel, formalisation; porteur: essais appareils et décision finale. Les observations historiques ne constituent pas des anomalies actuelles sans retest. Aucun taux global calculable sur les 20 contrôles hétérogènes.

## Preuves à récupérer
Archive Apple et SHA-256 complet, journaux Android, matrices de criblage initial/corrigé, captures, journaux locaux 24/58/65 et preuves de résolution, correspondance des commits et versions déployées. Conserver séparément des 494 workflows et 211 cas CI. Ne pas publier données personnelles ou matrices privées sans contrôle des droits.

Sources complémentaires indiquées dans le rapport: https://github.com/LMSEIF-UH2C/acpa-msmda ; https://github.com/LMSEIF-UH2C/acpa-msmda/pull/16 ; https://acpa-msmda.streamlit.app/ ; https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/ ; https://play.google.com/ ; https://www.prisma-statement.org/ ; Petersen et al. (2015), référence exacte à réconcilier.
