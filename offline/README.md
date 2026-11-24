# ACPA/MSMDA Terrain — socle expérimental hors ligne

Ce compagnon autonome est facultatif. Il ne remplace pas l'application Streamlit et ne conditionne pas la finalisation pédagogique du projet.

Périmètre actuel : chronomètre, scores, consultation d'une sauvegarde du cahier journalier, observations locales et export JSON. Le premier chargement et la mise en cache nécessitent une connexion et un hébergement HTTPS (ou localhost pour le développement). La persistance dépend du navigateur ; exporter les données avant effacement ou changement d'appareil. Aucune synchronisation automatique ni réintégration des observations n'est disponible. Ne pas saisir de données nominatives.

Pour un essai local, exécuter `python -m http.server 8000` depuis la racine du dépôt puis ouvrir `http://localhost:8000/offline/`. Vérifier la mise en cache avant de couper la connexion. La compatibilité réelle iOS/Android et la disponibilité hors ligne ne sont pas encore certifiées.

Chantiers futurs : déploiement public HTTPS, tests physiques multi-appareils, synchronisation contrôlée, intégration au journal et extension du catalogue hors ligne. Référence : https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation
