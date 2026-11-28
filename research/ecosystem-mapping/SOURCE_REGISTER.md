# Registre des sources — état exploratoire 28 novembre 2026

| Source | Accès et portée | Statut | Limites et vérifications |
|---|---|---|---|
| Apple Search API | https://performance-partners.apple.com/search-api ; recherche par terme, boutique, entité | Pilote 48/48 réussi | Plafonds, classement opaque, pas d'exhaustivité; vérifier réutilisation et icônes avant publication |
| F-Droid | https://f-droid.org/en/docs/All_our_APIs/ ; https://f-droid.org/repo/index-v2.json | Pilote index officiel lancé via workflow | Un dépôt, pas tout Android; index de métadonnées, pas d'APK; empreinte locale; signature de l'index non contrôlée par ce pilote; droits des champs et images à examiner |
| Google Play | https://developers.google.com/android-publisher/play-catalog | Éligibilité non confirmée | Ne pas présumer l'accès au catalogue; ne pas contourner les restrictions |
| Aptoide | https://webservices.aptoide.com/webservices/docs | À vérifier | Conditions, pagination, provenance, identifiants et disponibilité |
| GitHub | https://docs.github.com/en/rest/search/search | À préparer | Quotas et plafond de résultats, dépôts distincts des produits, licences spécifiques |
| Annuaires / éditeurs | accès documentaire ou interface autorisée | À documenter | Pas de collecte massive sans droit d'accès; critères de couverture et de sélection |
| Publications | sources bibliographiques | À documenter | Identifier produits et preuves d'efficacité distinctement |

Le registre ne constitue pas une autorisation de redistribution. Pour chaque source, documenter date, version des conditions, autorisation applicable, limites, erreurs, champs et politique de conservation. Pas d'accès à des identifiants privés, ni contournement des quotas.

## Mise à jour du 28 novembre — autorisations et audit
GitHub: pilote réussi, 471 dépôts distincts, 16 requêtes tronquées; voir AUDIT_GITHUB_PILOT.md.
Aptoide: API v7 apps/search documentée comme Public (https://ws75.aptoide.com/api/7/apps/search?info=1), mais les conditions générales https://en.aptoide.com/company/legal restreignent l'accès automatisé. Ne pas conclure que Public signifie autorisation de collecte massive ou de redistribution. Suspendre les appels automatisés jusqu'à clarification écrite ou licence/conditions spécifiques applicables. Documentation partenaires https://partners-center-be.aptoide.com/partners_api_doc/en. Aucune nouvelle requête de collecte Aptoide n'a été lancée ici. Préparer demande précisant finalité scientifique, champs, volumes, cadence, conservation et publication d'agrégats, pas d'APK ni de logos sans droit. Même exigence de vérification des droits et conservation pour les autres sources.

## Canaux complémentaires — 28 novembre
Voir [registre Web/desktop et preuves](CANAUX_COMPLEMENTAIRES_V01.csv). Wikidata CC0 pour données structurées; Flathub/AppStream et Snap recherche documentée, droits à vérifier; Microsoft Store accès catalogue non confirmé. Aucun pilote réseau supplémentaire.

## SILL / DINUM — 28 novembre 2026
https://code.gouv.fr/sill/ ; https://code.gouv.fr/sill/terms : données JSON publiées sous Licence Ouverte 2.0; accès aux fiches complètes réservé, export public à identifier et tester. Biais institutionnel français et libre. Pas de collecte effectuée à ce stade.

## SILL v2 — protocole de lancement 28 novembre 2026
Export public documenté https://code.gouv.fr/sill/api/v2/catalogi.json ; contrat https://code.gouv.fr/sill/api/docs ; licence et attribution DINUM. Ancien export trop volumineux pour lecture directe; pilote GitHub Actions préparé, état réseau non vérifié. Données partiellement issues de Wikidata; dépendance intersource. Voir SILL_PILOT_PROTOCOL.md. Aucun brut publié avant revue des champs.

SILL v2 : HTTP 500 au run 46139236521, six tests réussis, aucun résultat réseau. Export historique public /api/catalogi.json testé séparément après amendement; résultats à vérifier.

SILL export historique : run 46139311316 réussi, 672 entrées dont 615 non déréférencées, 57 déréférencées. Inventaire et empreintes disponibles dans l'artefact 15260778228; données brutes non conservées. Voir AUDIT_SILL_PILOT_V01.md. Aucune qualification pédagogique ni fusion.

Wikidata : pilote P31 direct sur dix classes, accès CC0, WDQS borné et arrêt sur erreur; plan et protocole versionnés. Résultats non vérifiés au lancement. QID SILL non présents dans projection, aucune indépendance présumée.

Wikidata : run 46139718701 réussi, 10/10 requêtes, 549 observations, 547 QID distincts, 2 plafonds; artefact 15261401982, CC0, audit AUDIT_WIKIDATA_PILOT_V01.md. Couverture P31 directe limitée, provenance SILL/Wikidata non résolue.

Complément documentaire 28 novembre : 17 observations issues de documentation officielle éditeurs et manuels, accès public ponctuel; registre PROSPECTION_MATERIEL_COMMERCIAL_V01.json. Fonctions déclarées, droits par source, pas de reproduction intégrale ni scraping. Validation indépendante et disponibilité Maroc non établies.

Revue documentaire 28/11 : [registre des droits V0.2](RIGHTS_DECISION_REGISTER_V02.md), décisions P2-15 à approuver; aucun nouvel accès source.
