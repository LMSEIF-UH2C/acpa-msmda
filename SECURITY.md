# Sécurité de la démonstration ACPA/MSMDA

## Périmètre et modèle de menace
Cette interface est une démonstration publique **sans authentification**. Tout visiteur peut soumettre une courte description fictive au moteur local. Elle n'est **pas** autorisée pour les données d'élèves, dossiers médicaux, identifiants ou informations confidentielles. Une publication sur Streamlit Community Cloud n'est pas une certification de sécurité.

## Mesures déjà présentes
- Aucun compte, secret, jeton API, appel vers une API tierce ou base de données n'est requis par l'interface.
- Le moteur lit un catalogue local explicitement synthétique et n'accepte pas de chemin de catalogue fourni par l'utilisateur.
- Champ de saisie plafonné à 1 000 caractères, avec refus des saisies vides.
- Les résultats sont conservés dans la session Streamlit, sans sauvegarde applicative persistante.
- Pas de rendu HTML utilisateur ni d'exécution de code fourni par les visiteurs.
- Dépendance Streamlit épinglée et vérification automatique sur chaque changement.
- Protection XSRF et CORS activées dans la configuration Streamlit.

## Risques résiduels
- Les textes saisis et métadonnées réseau transitent vers l'hébergeur. Ne jamais promettre une confidentialité absolue.
- Sans authentification ni quota réseau en amont, une application publique peut subir des abus ou une saturation.
- La dépendance épinglée doit être régulièrement mise à jour et contrôlée contre les vulnérabilités connues.
- Aucun audit de pénétration, revue d'infrastructure ou test de charge n'a été réalisé.
- Les scores et profils fictifs ne sont pas validés pour une décision pédagogique réelle.
- Le contenu du JSON exporté peut inclure le contexte soumis ; n'y saisir aucune donnée personnelle.

## Contrôles avant mise en ligne
1. Vérifier que seule la branche publique approuvée est déployée ; ne jamais déployer `acpa-msmda-dev`.
2. Vérifier qu'aucun secret ni fichier de données réelles n'est ajouté au dépôt.
3. Activer les protections de branche, la revue de PR et les alertes Dependabot dans GitHub selon les droits disponibles.
4. Examiner les politiques et journaux de l'hébergeur et limiter l'accès si des utilisateurs pilotes sont impliqués.
5. Tester FR, EN, AR, saisie vide, limite de longueur, export JSON et mobile.
6. Pour une version avec données personnelles : authentification, autorisations, chiffrement, rétention, sauvegardes, politique de confidentialité et revue juridique préalables.

## Signalement
Signaler les vulnérabilités en privé aux mainteneurs du dépôt. Ne pas publier d'exploit ou de données sensibles dans les issues publiques.

Sources :
- https://docs.streamlit.io/develop/concepts/configuration/https-support
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- https://docs.github.com/en/code-security
