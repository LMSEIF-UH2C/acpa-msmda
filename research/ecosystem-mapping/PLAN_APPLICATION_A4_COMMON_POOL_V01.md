# A4 — Comparaison sur pool commun et oracle étendu V0.1
Protocole de recette technique prospective, distinct de la validation scientifique. Aucun résultat anticipé. Référence : PLAN_APPLICATION_A4_V01.md, COVERAGE_TARGETED_PLAN_V02.json et COUVERTURE_FONCTIONS_V01.csv (référentiel proposé non validé).
## Deux expériences non interchangeables
- H : sortie native réelle de real_catalog.recommend, texte FR/AR/EN et catalogue figé par SHA256, votes neutres. Conserver rang, fit et correspondances sans transformer un mot-clé en fonction prouvée. Sans correspondance identité/variante, fonction/contextes et coût validés, métriques communes = null. Ne pas confondre absence de preuve et violation.
- T : comparaison sur un pool de candidats fictifs explicitement marqués TEST_FIXTURE. Même contexte, mêmes portes individuelles, mêmes règles de combinaison. I = meilleure configuration admissible de taille 1; P = meilleure configuration de taille 1 ou 2; E = meilleur ensemble admissible sans plafond de taille (borne de recherche explicite). I/P sont des comparateurs optimisés et non des reproductions du moteur H. Ne jamais comparer un score fit de H à une couverture T.
## Dix cas de référence à construire
Chaque scénario reprend les IDs de fonctions proposées; choix de fonctions obligatoires/facultatives et valeurs de coûts/appareils sont conventions de test, pas décisions didactiques. Chaque outil est fictif; aucun nom commercial, aucune preuve fabriquée.
| Scénario | Obligatoires | Facultatives | Contraste à tester |
|---|---|---|---|
| S01 relais | F04 F06 F07 | F05 | besoin de trois outils complémentaires, séquences et hors ligne |
| S02 orientation | F01 F02 F08 F13 | — | budget et exclusion réseau inconnu |
| S03 activités adaptées | F04 F09 F13 | F05 | accessibilité inconnue |
| S04 gymnastique | F04 F05 | F07 | sécurité physique inconnue, pas de gain obligatoire de l'immersion |
| S05 vitesse | F03 F06 F07 | F10 | confidentialité et dépendances |
| S06 badminton | F04 F11 F12 | — | coût/période comparables, réseau |
| S07 basketball | F02 F08 F15 | — | doublon produit et incompatibilités |
| S08 course en durée | F03 F06 | F10 | capteur/appareil non disponible |
| S09 volleyball | F01 F10 F14 | — | ressources simultanées et séquentielles |
| S10 jeux traditionnels | F01 F02 F05 F09 | F11 F12 | contraintes non modélisées et abstention |
## Oracle et critères d'acceptation
Construire un oracle indépendant par masque binaire, sans réutiliser _reason, _combination, _result ou le tri du solveur. Pour les petits pools, vérifier éligibilité, budget cumulé, période, appareils par phase, identité distincte, dépendances, incompatibilités et couverture. Vérifier séparément I/P/E selon le rang lexicographique (-couverture obligatoire, nombre, charge, coût, IDs), la sélection E seulement si couverture obligatoire complète. Tester permutations des candidats, bornes de calcul, absence de configuration, contraintes inconnues, et un échantillon pseudo-aléatoire déterministe de petits pools. Publier les divergences et échecs, y compris absence de gain et surcoût de E. En cas de recherche incomplète, comparateurs définitifs absents. Mesurer couverture obligatoire/facultative, nombre d'outils, coût, charge et besoins non couverts, sans effet causal ni comparaison réelle H/T.
## Avant A5
Les CI de la branche expérimentale doivent être terminales et réussies au commit exact. L'interface peut présenter un mode démonstration fictif et un mode documentaire abstention, clairement distincts; aucune recommandation opérationnelle issue des 34 pistes. Un comparateur historique réellement apparié reste conditionné à une table identité/fonctions/preuves indépendante et aux autorisations scientifiques. Ne pas lever ce verrou par un test synthétique.

## Acceptation applicative A6 — décision du porteur
Recette interne documentée et acceptation du porteur, sans nouveau panel obligatoire pour l'application expérimentale. Les preuves contextuelles, critères de sécurité et limites scientifiques restent exigibles; aucune validation humaine indépendante simulée, aucun changement des gates confirmatoires.
