# ACPA/MSMDA 2.0 — Plan d'action opérationnel

## Architecture cible
1. **Moteur ACPA/MSMDA** : recommandations technopédagogiques et critères scientifiques existants.
2. **Catalogue d'applications** : tracking (Strava), gymnastique, analyse vidéo, parcours pédagogiques (Symbaloo), capteurs, évaluation ; fiches sourcées et vérifiées.
3. **Performance Lab** : épreuves physiques institutionnelles, mesures de thèse, tests psychomoteurs, psychométriques et observation ALT-PE.
4. **Planificateur EPS** : APS, niveau, durée, effectif, matériel, ateliers, rotations.
5. **Pilotage** : chronomètres, engagement moteur, attente, transitions.
6. **Bilans** : indicateurs, comparaisons de séances, exports et historique sécurisé.

## Livraison 1 — Cette branche
- Référentiel initial de 19 tests et mesures, dont les huit épreuves et trois mesures associées décrites au tableau 3 de la thèse V182.
- Page Streamlit Performance Lab avec recherche par domaine/source, saisie sans nom, calcul Cooper limité à la formule explicitée, export CSV.
- Les tests sans équation/protocole complet restent des fiches de saisie ; aucune valeur ou norme inventée.
- Aucune persistance serveur ou synchronisation Massar.

## Livraison 2 — Après revue de la PR
- Vérifier la circulaire primaire et chaque protocole (variantes, unités, nombres d'essais, règles de calcul).
- Ajouter moteur de chronométrage et protocole Léger avec version et signaux.
- Relier les résultats de tests aux objectifs pédagogiques sans confondre mesure physique et performance enseignante.
- Étendre le catalogue d'applications et le rendre interrogeable par ACPA/MSMDA.

## Livraison 3 — Pilote
- Sécurité et consentement, pseudonymisation, rôles, stockage chiffré, politique de rétention.
- Tests fonctionnels et terrain, accessibilité mobile, FR/AR/EN.
- PDF, historique et comparaisons longitudinales seulement après dispositif de protection des données.

Sources à confronter : thèse V182, tableau 3 et études 5–6 ; circulaire MENPS n°2358/25 du 26 novembre 2025 ; https://www.frmss-dpss.com/ .
