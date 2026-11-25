# Statut scientifique des composantes de v0.2.0

Ce document distingue le prototype ACPA/MSMDA évalué dans les travaux doctoraux du porteur du projet et l'implémentation publique v0.2.0. Aucune fonction de v0.2.0 n'est présentée comme validée expérimentalement. Seules certaines composantes antérieures ont fait l'objet d'une évaluation doctorale, sur une autre implémentation.

## 1. Deux implémentations distinctes

| | Prototype doctoral (Étude 4) | Application publique v0.2.0 |
|---|---|---|
| Extraction du contexte | chaîne multilingue avec détection de langue, lemmatisation, dictionnaires EPS spécialisés, pondération TF-IDF et similarité par plongements | règles déterministes : normalisation du texte (y compris l'arabe), vocabulaire contrôlé, quatre indicateurs de contexte |
| Données évaluées | base de 127 outils notés sur les 18 critères | répertoire réel de 2 466 fiches issues de la cartographie (section 3) |
| Architecture | modules en ligne et hors ligne, base distante et base locale | service web Streamlit, données de session temporaires, sauvegardes Excel |
| Calcul du score | section 2.1 | section 2.2 |
| Résultats empiriques | F1 = 0,87 sur 200 requêtes de test ; concordance de 82,2 % avec des évaluations d'experts sur 157 situations, κ = 0,76 ; score 10D/97P global de 4,11/5 (6 experts, α de Krippendorff = 0,79) ; SUS = 78,3 (ET = 8,2 ; N = 24 enseignants, région Casablanca-Settat) | aucun résultat empirique propre ; vérifications techniques seulement (section 4) |

Les résultats du prototype appartiennent à l'implémentation évaluée et à ses conditions de test. Ils **ne sont pas transposables** à v0.2.0 et ne doivent pas lui être attribués dans une publication, un dépôt ou une présentation.

## 2. Formule de score

### 2.1 Prototype doctoral

Score composite d'un outil i : Sᵢ = Σⱼ αⱼ Cᵢⱼ sur les 18 critères, avec Σ αⱼ = 1 ; pénalité de sécurité Sᵢ × (1 − β × risqueᵢ), β = 0,15 ; normalisation min-max sur l'ensemble des outils, ramenée à 100.

### 2.2 Implémentation v0.2.0 (`src/acpa_msmda/scoring.py`, inchangé)

Le catalogue réel comporte des critères non renseignés (« NR », la description de l'éditeur n'en dit rien) et des critères sans objet (« SO »). La formule a été adaptée à ces données manquantes :

S = (Σⱼ αⱼ Cⱼ + m × 5) / (Σⱼ αⱼ + m) × (1 − β × risque) × 10

- Les sommes ne portent que sur les critères notés de la fiche.
- m = 0,30 rapproche une fiche peu documentée de la note neutre 5/10, au lieu de la traiter comme nulle ou excellente.
- β = 0,15, comme dans le prototype.
- Pas de normalisation min-max : le score d'une fiche ne dépend pas des autres fiches du catalogue.
- Une fiche dont l'alignement avec les programmes d'EPS (C13) est sans objet ou au plus 2/10 n'est pas recommandée.

Les poids αⱼ partent d'une répartition égale (1/18) et sont majorés par quatre indicateurs de contexte (connexion faible, grand effectif, budget serré, inclusion ; `CONTEXT_BOOSTS` dans `src/acpa_msmda/context_engine.py`), puis renormalisés à une somme de 1. Ces majorations sont heuristiques. Elles n'ont pas été calibrées par une procédure d'experts.

### 2.3 Valeur affichée à l'enseignant

L'interface affiche un **indice d'adéquation** sur 100, distinct du score MSMDA. Il est calculé dans `src/acpa_msmda/real_catalog.py`, fonction `recommend` :
- 50 points au plus pour la correspondance entre la demande et la fiche (activité, usages) ;
- la moitié du score de la section 2.2, ou 50 si la fiche n'est pas notée ;
- des bonifications : fiche vérifiée +3 ; demande hors connexion et outil utilisable hors connexion +4 ; demande en arabe et application en arabe +4 ; demande gratuite et application gratuite +4 ; avis des enseignants de −6 à +6 ;
- le tout borné entre 0 et 100.

Les mentions affichées le qualifient d'« indice heuristique de correspondance, non validé comme mesure d'efficacité pédagogique ».

## 3. Cartographie des applications

Chiffres de référence, d'après le diagramme de flux définitif de la cartographie (inspiré de PRISMA 2020) :

| Étape | n |
|---|---|
| Enregistrements identifiés dans les magasins (App Store 23 194 ; Aptoide 17 456 ; F-Droid 5 026) | 45 676 |
| Doublons supprimés (nom normalisé) | 4 917 |
| Enregistrements criblés, après dédoublonnage | 40 759 |
| Exclus au criblage | 30 694 |
| Évalués pour l'éligibilité | 10 065 |
| Éligibles | 2 913 |
| Inclus : version 1 (900), double criblage indépendant (1 123 sur 1 876 ; κ = 0,685, IC 95 % [0,652 ; 0,718]), autres sources (204 + 162 + 77) | 2 466 |

Le répertoire de v0.2.0 compte 2 466 fiches, conformément à ce diagramme (`tests/test_catalog_header.py`). Le chiffre « plus de 43 000 applications », relevé dans des échanges antérieurs, ne correspond à aucune étape du diagramme et ne doit plus être utilisé.

Notes des 18 critères par fiche (`criteria_method`) :
- 2 354 fiches par estimation à partir de la description de l'éditeur ;
- 100 fiches par double notation indépendante ;
- 12 fiches dont les fonctions ont été vérifiées.

Les fonctions de 5 fiches sont vérifiées sur le site officiel et celles de 7 autres sont relevées sur une source officielle.

## 4. Statut de chaque composante

| Composante | Statut dans v0.2.0 | Fondement |
|---|---|---|
| Cadre 10D/97P (10 dimensions, 97 paramètres) | évalué dans les travaux doctoraux (Étude 3 : α de Krippendorff = 0,82) ; non implémenté comme grille dans v0.2.0 | travaux doctoraux et article publié |
| Prototype ACPA/MSMDA | évalué dans les travaux doctoraux (Étude 4) ; résultats non transposables | section 1 |
| 18 critères MSMDA | mêmes intitulés et même ordre que le prototype | `src/acpa_msmda/catalog.py` |
| Répertoire de 2 466 applications | issu de la cartographie ; notes majoritairement estimées | section 3 |
| Moteur de score et indice d'adéquation | vérifiés techniquement (tests automatisés) ; non validés empiriquement | sections 2.2 et 2.3 |
| Statistiques du Laboratoire | vérifiées techniquement : 29/29 métriques concordantes avec R 4.5.2 | `docs/validation/` |
| 32 instruments du Laboratoire | documentés bibliographiquement ; conformité intégrale aux protocoles d'origine non attestée | `docs/LAB_REFERENCE_AUDIT.md` |
| Espace EPS, cahier journalier, évaluation formative, Studio, mode terrain, illustrations | fonctions complémentaires conçues à partir des besoins, obstacles et pratiques des enseignants ; non évaluées empiriquement | conception |
| Méta-analyse et études empiriques 1, 2, 5 et 6 | fondements de la démarche ; leurs résultats ne sont ni reproduits ni revendiqués par l'application | travaux doctoraux |

## 5. Formulations à employer

À employer : « démonstrateur de recherche », « vérifié techniquement », « indice heuristique », « notes estimées à partir de la description de l'éditeur ».

À proscrire pour v0.2.0 : « validé scientifiquement », « efficacité démontrée », toute reprise des résultats F1, κ ou SUS du prototype.
