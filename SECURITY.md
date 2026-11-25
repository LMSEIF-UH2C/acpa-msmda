# Sécurité de la démonstration ACPA/MSMDA

État au 25 novembre 2026, version 0.2.0.

## Périmètre et modèle de menace

L'application publique est un démonstrateur de recherche **sans authentification**. Tout visiteur peut décrire un contexte d'enseignement, consulter le répertoire, préparer des séances et charger certains fichiers. Elle n'est **pas** autorisée pour les données d'élèves (noms, codes Massar, dates de naissance), les dossiers médicaux, les identifiants ou les informations confidentielles. Une publication sur Streamlit Community Cloud n'est pas une certification de sécurité.

## Mesures en place

**Données et stockage**
- Aucun compte, secret, jeton d'API ni base de données n'est requis.
- Les données saisies restent dans la session Streamlit du serveur, de façon temporaire ; il n'y a pas de sauvegarde applicative persistante. L'enseignant conserve ses données en téléchargeant des classeurs Excel.
- Le répertoire de 2 466 applications réelles (`data/real_tools_catalog.json`) est lu localement ; l'interface n'accepte aucun chemin de fichier fourni par l'utilisateur.
- Les interfaces invitent à utiliser des codes de groupe non nominatifs et à ne saisir ni nom ni identifiant d'élève.

**Fichiers chargés (5 champs)**

| Champ | Formats | Contrôles |
|---|---|---|
| Reprise des évaluations formatives | XLSX | 10 Mo au plus ; feuilles et colonnes attendues seulement ; refus des formules, macros, liens externes, cellules d'erreur, de date ou booléennes ; limite d'expansion de l'archive et de nombre de lignes |
| Restauration du cahier journalier | XLSX | mêmes contrôles |
| Restauration des projets de cycle | XLSX | mêmes contrôles |
| Import d'une étude dans le Laboratoire | CSV ou XLSX | 4 Mo et 30 000 lignes au plus ; classeur limité à une seule feuille, refus des cellules contenant une formule, limite d'expansion de l'archive ; mêmes colonnes et contrôles que le CSV |
| Photo d'une situation (Studio) | JPEG ou PNG | 5 Mo au plus ; image décodée, réduite à 1 600 px au plus puis réencodée en JPEG dans une image neuve, ce qui retire ses métadonnées (dont la géolocalisation) ; refus des images au nombre de pixels excessif |

La taille maximale de chargement est fixée à 10 Mo dans `.streamlit/config.toml`.

**Exports**
- Les textes commençant par `=`, `+`, `-` ou `@` sont écrits dans les classeurs comme du texte, jamais comme des formules.
- Les exports JSON et CSV sont réservés aux usages scientifiques avancés du Laboratoire.

**Interface et configuration**
- Le HTML injecté se limite à des feuilles de style statiques et à des libellés traduits ; aucun contenu saisi par l'utilisateur n'est rendu en HTML.
- La dictée vocale s'exécute dans le navigateur (reconnaissance vocale du navigateur) ; l'application ne reçoit que le texte transféré dans le champ.
- Protection XSRF et CORS activées ; collecte de statistiques d'usage Streamlit désactivée.
- Toutes les dépendances sont épinglées dans `requirements.txt` et la suite de tests est exécutée sur chaque modification (Python 3.12 et 3.14).

## Risques résiduels

- Les textes saisis, la voix traitée par le service de reconnaissance du navigateur et les métadonnées réseau transitent par l'hébergeur ou le fournisseur du navigateur. Ne jamais promettre une confidentialité absolue.
- Sans authentification ni quota en amont, une application publique peut subir des abus ou une saturation.
- Les dépendances épinglées doivent être mises à jour et contrôlées régulièrement contre les vulnérabilités connues.
- Aucun audit de pénétration, revue d'infrastructure, test de charge ni audit d'accessibilité n'a été réalisé.
- Les notes et indices du répertoire sont heuristiques et majoritairement estimés ; ils ne sont pas validés pour une décision pédagogique réelle (voir `docs/statut-scientifique-v0.2.0.md`).
- Un classeur restauré n'est pas authentifié : il peut avoir été modifié hors de l'application dans les limites des contrôles ci-dessus.

## Contrôles avant mise en ligne

1. Vérifier que seule la branche `main` approuvée est déployée et que la révision déployée correspond au commit publié.
2. Vérifier qu'aucun secret ni fichier de données réelles n'est ajouté au dépôt.
3. Activer les protections de branche, la revue de PR et les alertes Dependabot selon les droits disponibles.
4. Examiner les politiques et journaux de l'hébergeur ; limiter l'accès si des utilisateurs pilotes sont impliqués.
5. Tester FR, AR, EN, saisie vide, limites de longueur, sauvegarde et restauration Excel, exports PDF et affichage mobile.
6. Pour une version avec données personnelles : authentification, autorisations, chiffrement, rétention, sauvegardes, politique de confidentialité et revue juridique préalables (loi 09-08 au Maroc).

## Signalement

Signaler les vulnérabilités en privé aux mainteneurs du dépôt. Ne pas publier d'exploit ou de données sensibles dans les issues publiques.

Sources :
- https://docs.streamlit.io/develop/concepts/configuration/https-support
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- https://docs.github.com/en/code-security
