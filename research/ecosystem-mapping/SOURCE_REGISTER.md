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
