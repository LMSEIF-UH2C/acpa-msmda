# Audit du pilote Wikidata v0.1

## Clôture technique Wikidata — 28 novembre 2026 UTC
[Run 46139718701](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46139718701), commit 0f9389d34f58271bb513748dc1137ea2bf0cdb78 : six tests synthétiques réussis, téléchargement de l'inventaire SILL réussi, dix requêtes sur dix HTTP 200. Exécution réseau 11:24:23–11:24:46 UTC. 549 observations classe-QID, 547 QID distincts (2 observations redondantes), deux plafonds atteints sur dix. 
| Classe | QID observés | Plafond atteint |
|---|---:|---|
| Logiciels éducatifs | 101 | Oui |
| LMS | 75 | Non |
| Statistiques | 23 | Non |
| Cartographie | 87 | Non |
| Vidéo | 101 | Oui |
| Bibliographie | 57 | Non |
| Bureautique | 83 | Non |
| Fitness | 9 | Non |
| Casques VR | 1 | Non |
| Assistants IA générative | 12 | Non |
| Total observations | 549 | 2 |
547 QID distincts : 484 labels EN, 254 FR, 92 AR (non exclusifs; ne pas assimiler à langues d'interface). 13 QID avec candidat nominal dans catalogue 2466, 15 avec candidat SILL 672, 1 dans les deux; union 27, 520 sans candidat dans ces deux projections. Aucun lien d'identité confirmé. QID SILL absents de la projection, dépendance partielle SILL/Wikidata non quantifiée. Les résultats très faibles VR/fitness reflètent possiblement la modélisation P31 directe et non la rareté du marché; le QID de casque VR choisi peut être trop restrictif, examiner les classes voisines et modèles connus. Les deux classes plafonnées exigent décision de complément ciblé; un résultat sous plafond ne couvre pas les sous-classes ou entités mal typées. Aucun score, aucune intégration ni estimation de nouveauté nette.
Preuve : [artefact 15261401982](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46139718701/artifacts/15261401982), 31 782 octets, digest ZIP sha256:e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46, expiration 28 décembre 2026; journaux et métadonnées vérifiés, archive non recalculée indépendamment. Les dix réponses brutes structurées CC0, requêtes, manifeste et inventaire sont produits par le workflow; vérifier leur contenu et empreintes avant archivage pérenne.
La [matrice de clôture](MATRICE_CLOTURE_PHASE2_V01.md) reste ouverte. Prochain bloc : sécurisation des preuves et audit hors ligne des inventaires SILL/Wikidata (effectifs, empreintes disponibles, recouvrements, témoins), puis plan ciblé matériel/AR et Web commercial avec accès autorisés. Ne pas élargir sans lacune justifiée. Préconditions humaines, archives historiques, droits et préenregistrement toujours ouvertes; collecte définitive non lancée.
