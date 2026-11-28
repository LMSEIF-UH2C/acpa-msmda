# A4 — Contrat de décision écosystémique (préparation technique V0.1)
Proposition technique, pas de préenregistrement ni de validation scientifique. Piste application PR82, distincte des phases confirmatoires de recherche. Ne pas implémenter avant clôture A3. Conserver le parcours historique stable par défaut et les 2466 références inchangées. Les 34 propositions A3 sont non évaluées indépendamment, contraintes inconnues : aucune admission automatique. Le moteur peut être testé avec fixtures fictives explicitement identifiées, sans produire de recommandation réelle validée.

## Entrées et unités
- Situation EPS : APS, niveau, objectif, phases, fonctions nécessaires et facultatives (référentiel F01–F15 proposé), contexte K01–K12. Pas d'inférence de besoin obligatoire à partir du nom d'une activité.
- Technologie : variante et identité documentées, fonctions attestées par preuve pertinente pour la situation, identifiant d'observation et hash de source locale, état de revue, compatibilité du contexte. Une piste documentaire n'est pas une technologie admissible.
- Configuration : ensemble de variantes et dépendances explicites, attribution des fonctions, séquence avant/pendant/après, coût total, équipement partagé ou simultané, charge de mise en œuvre. Ne pas compter deux fois un produit sous des alias; cas d'identité ambiguë non admis opérationnellement.
- Une absence de preuve, une contrainte inconnue et une incompatibilité sont trois états distincts. Ne pas substituer un score de popularité, un SPED non validé ou une note moyenne à la preuve.

## Règles techniques à implémenter et à éprouver
1. Vérifier l'éligibilité individuelle sur preuves valides et revue autorisée; connexion hors ligne si exigée, âge/confidentialité, sécurité, disponibilité, appareils, accessibilité requise. Inconnu critique = exclusion de la recommandation opérationnelle, mais maintien dans registre.
2. Vérifier les contraintes de combinaison : coût cumulé exprimé en MAD avec période et frais obligatoires explicites; budget nul = aucun coût obligatoire connu non nul; dépendances présentes; incompatibilités explicites; équipement simultané disponible. Ne pas prétendre interopérabilité sur simple co-présence. Une combinaison nécessitant échange automatique exige preuve de compatibilité; sinon transfert manuel seulement si explicitement documenté et faisable. Les exigences non modélisées sont bloquantes, pas ignorées.
3. Rechercher une couverture des fonctions obligatoires, puis minimiser nombre d'outils et charge documentée; départage déterministe, coût total et couverture facultative affichés. Ordre lexicographique proposé pour le prototype à discuter, sans poids scientifique adopté. Comparer à un outil individuel et une combinaison simple sur le même pool admissible et mêmes contraintes. Pas de résultat complet si une fonction obligatoire manque. Renvoyer besoins non couverts, raisons d'exclusion et alternatives non numériques en tant que pistes, sans présenter les alternatives comme vérifiées.
4. Limiter la recherche combinatoire par borne explicite; si limite atteinte, statut INCOMPLETE_SEARCH et pas de prétention d'optimum global. Sur petites fixtures, vérifier contre énumération exhaustive de référence indépendante. Aucun score d'efficacité pédagogique.
5. Séparer sorties TEST_FIXTURE, PROPOSITION_EXPERIMENTALE et absence de recommandation; aucun résultat synthétique visible comme conseil réel. Interface A5 seulement après recette A4, tests externes A6 et décision avant publication.

## Cas de référence proposés avant exécution (non exécutés)
Les cas s'appuient sur COVERAGE_TARGETED_PLAN_V02.json et COUVERTURE_FONCTIONS_V01.csv, scénarios pédagogiques non validés par programme officiel. Les outils des tests seront fictifs. Tous les résultats ci-dessous sont des attentes.
| ID | Situation / test | Résultat attendu |
|---|---|---|
| A4-T01 | Relais S01, téléphone enseignant seul, réseau absent | Exclure les variantes en ligne ou hors ligne inconnu; rendre besoins non couverts si nécessaire. |
| A4-T02 | Deux outils couvrent des besoins complémentaires | Combinaison complète minimale, rôle distinct pour chacun. |
| A4-T03 | Un outil couvre tous les besoins obligatoires | Préférer un outil seul plutôt qu'une combinaison redondante. |
| A4-T04 | Deux outils individuellement sous budget mais somme supérieure | Rejeter la combinaison. |
| A4-T05 | Coût obligatoire inconnu ou période non comparable | Ne pas déclarer compatible avec budget plafonné. |
| A4-T06 | Dépendance manquante ou non admissible | Exclure la configuration, expliquer dépendance. |
| A4-T07 | Deux variantes incompatibles ou nécessitant même appareil au même moment | Exclure combinaison incompatible; distinguer usage séquentiel. |
| A4-T08 | S04 gymnastique/immersion, risque physique inconnu | Aucun outil immersif recommandé dans ce contexte. |
| A4-T09 | S05 vidéo/IA, autorisation et traitement local non établis | Exclusion opérationnelle, pas de contournement. |
| A4-T10 | Identité incertaine ou même produit sous deux alias | Pas de double comptage ni de fusion automatique. |
| A4-T11 | Source locale modifiée à URL/date identiques | Ne pas utiliser l'ancienne preuve/proposition. |
| A4-T12 | Les 34 pistes A3 réelles, aucune compatibilité établie | Zéro recommandation opérationnelle nouvelle; explication, pas de score. |
| A4-T13 | Plusieurs solutions égales / ordre des entrées permuté | Résultat déterministe et transparent. |
| A4-T14 | Limite de recherche atteinte | INCOMPLETE_SEARCH explicite; aucun optimum affirmé. |
| A4-T15 | Oracle exhaustif sur petits ensembles de fixtures | Vérifier couverture, contraintes et parcimonie. |
| A4-T16 | Comparaison individuel / combinaison simple / moteur | Même contexte et même ensemble admissible; conserver échecs/absences de gain. |

Mesures techniques : couverture obligatoire et facultative, violations dures (attendu zéro), nombre d'outils, coût documenté, charge, besoins non couverts, raisons, temps/limites de recherche. Les cas sont conçus pour éprouver le comportement, pas pour estimer efficacité ou supériorité empirique. Toute divergence est conservée dans REGISTRE_ECHECS_ANOMALIES_LIMITES_V01.md. Aucun ajout au catalogue, aucune activation par défaut, aucun score ou collecte nouvelle par ce document.
