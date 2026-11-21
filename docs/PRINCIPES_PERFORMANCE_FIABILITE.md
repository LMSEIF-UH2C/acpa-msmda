# ACPA/MSMDA — Bonnes pratiques de performance et de fiabilité

> Synthèse de travail du 21 novembre 2026, proposée par le porteur du projet. **Document indicatif, non normatif.** Ne constitue ni une décision d'architecture, ni une preuve de conformité réglementaire, ni une exigence de mise en œuvre immédiate. Toute pratique doit être confrontée à l'architecture réelle, aux risques et aux essais de terrain.

## Finalité prioritaire

**Améliorer l'efficacité de l'enseignement de l'EPS en identifiant et intégrant les technologies les mieux adaptées au contexte.** Le moteur ACPA/MSMDA reste central. Le catalogue de technologies, le Performance Lab, la planification et l'observation sont des modules complémentaires ; la thèse fournit des fondements scientifiques mais ne limite pas le périmètre futur.

## Contexte d'usage à considérer

Terrain et gymnase, réseau faible ou absent, téléphones personnels modestes, classes de 30 à 45 élèves, séances de 55 minutes à 2 heures. Ces hypothèses doivent être validées par observation et essais utilisateurs, et non transformées en spécifications universelles.

## Priorités indicatives

1. **Fiabilité et hors ligne** : pouvoir consulter les protocoles et saisir des mesures sans réseau, avec statut explicite de sauvegarde. Ne pas promettre une synchronisation ou une conservation durable avant de les avoir réellement implémentées et testées.
2. **Réactivité des données** : limiter les requêtes N+1, récupérer les seules données nécessaires et indexer les colonnes utilisées dans les recherches fréquentes.
3. **Légèreté des médias** : formats compressés adaptés, images redimensionnées, pictogrammes vectoriels et vidéos chargées à la demande.
4. **Historique extensible** : afficher les classes usuelles sans pagination inutile ; paginer par curseur les grands historiques lorsque les volumes le justifient.
5. **Retours visuels utiles** : statuts de saisie et de synchronisation clairs ; indicateurs de chargement uniquement lorsque l'attente est perceptible.

## Options d'architecture à évaluer, non prescrites

- **Application mobile native / hybride** : base locale SQLite (Room, Drift ou autre), file d'écritures identifiées par UUID, synchronisation idempotente et mécanisme de reprise en arrière-plan adapté à la plateforme.
- **PWA / web** : IndexedDB ou autre stockage local adapté, service worker si applicable, capacités de synchronisation à vérifier selon navigateurs et appareils ; ne pas supposer la disponibilité universelle du background sync.
- **Streamlit actuel** : maintenir une démonstration sans données nominatives. Le stockage en mémoire de session n'est ni un mode hors ligne, ni une sauvegarde durable. La mise en place d'une véritable architecture offline-first exigera un choix et des tests techniques distincts.

### Gestion des conflits

- Données saisies sur un seul appareil : simplifier le parcours, mais ne pas appliquer aveuglément « dernier écrit gagnant » aux mesures, qui peuvent nécessiter une piste d'audit.
- Listes de classes partagées : stratégie de fusion ou d'arbitrage explicite.
- Notes finales, barèmes et corrections : conserver l'historique, signaler les conflits et solliciter une validation humaine.
- Toute synchronisation doit traiter les doublons, les reprises après coupure et les changements de schéma.

## Ergonomie de terrain

Saisie numérique directe, progression rapide entre élèves, contraste extérieur, grandes zones tactiles (repère initial : au moins 48 dp pour Android), peu d'étapes par mesure, indicateur visible des données en attente. Les objectifs de performance doivent être mesurés sur appareils et réseaux représentatifs : par exemple Android 2–3 Go de RAM, réseau 3G ou coupé, 45 élèves fictifs, historique annuel simulé.

## Confidentialité et conformité

Minimisation des données, pas de photographies d'élèves par défaut, contrôle d'accès, chiffrement adapté, HTTPS, politique de conservation, pseudonymisation des exports de recherche. Pour les mineurs et les mesures physiologiques, procéder à une analyse juridique spécifique avant collecte réelle. **Le régime de déclaration ou d'autorisation CNDP, la qualification de données de santé et les règles de transfert international doivent être confirmés auprès de la CNDP ou d'un conseil compétent ; ne pas présumer qu'une simple déclaration suffit, ni que tout transfert est automatiquement interdit.**

## Critères d'acceptation à définir avant chaque version

- Aucune perte silencieuse de saisie ; statut de conservation honnête.
- Calculs et unités testés par protocole ; aucune norme ou estimation non sourcée.
- Performance de consultation et de saisie mesurée sur un appareil modeste.
- Fonctionnement avec réseau coupé **uniquement si annoncé et réellement pris en charge**.
- Absence de collecte nominative en démonstration publique.
- Recommandations technologiques contextualisées, transparentes sur leurs preuves et incertitudes.

## Adoption progressive

**Immédiat (prototype Streamlit)** : transparence sur l'absence de persistance, tests de calcul, export, légèreté et interface de saisie.  
**Pilote terrain** : mesures d'ergonomie, définition du stockage et des exigences de sécurité.  
**Version mobile opérationnelle** : architecture locale durable, file de synchronisation, résolution des conflits et essais hors ligne avant toute promesse de fiabilité.

## Références à consulter

- Android Go : https://developer.android.com/guide/topics/androidgo/best-practices
- Android Go optimisation : https://developer.android.com/guide/topics/androidgo/optimize
- Android data cost : https://developer.android.com/docs/quality-guidelines/build-for-billions/data-cost
- Android touch targets : https://support.google.com/accessibility/android/answer/7101858
- web.dev accessible targets : https://web.dev/articles/accessible-tap-targets
- web.dev stale-while-revalidate : https://web.dev/articles/stale-while-revalidate
- MDN PWA caching : https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching
- Nielsen Norman Group skeleton screens : https://www.nngroup.com/articles/skeleton-screens/
- CNDP notification des traitements : https://www.cndp.ma/wp-content/uploads/2025/07/CNDP_Procedure-de-Notification-des-traitements_20250724.pdf

Ces sources constituent des points de départ à vérifier lors des décisions d'implémentation. Les propositions initiales sur la pagination, les images, les index, le cache, les squelettes et les mécanismes de synchronisation restent des pistes conditionnelles, non des obligations.
