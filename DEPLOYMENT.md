# Déployer l'application web ACPA/MSMDA

Application Streamlit destinée aux enseignants d'EPS : recherche de technologies
dans le catalogue réel, conception de séance, organisation des ateliers et
Performance Lab. Le moteur heuristique publié (`run_engine.py`) reste exécutable
séparément sur les profils fictifs de `data/synthetic_tools.json`.

## Lancement local

Pré-requis : **Python 3.12**, la version utilisée par l'intégration continue.
`requirements.txt` fixe la version exacte de chaque dépendance, y compris les
dépendances indirectes (Altair, narwhals, pandas…), pour que l'environnement
local, la CI et l'hébergement soient identiques.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

## Mise en ligne avec Streamlit Community Cloud

1. Examiner cette branche et fusionner la pull request après validation.
2. Aller sur https://share.streamlit.io et se connecter avec GitHub.
3. Choisir **Create app → Yup, I have an app**.
4. Renseigner le dépôt `LMSEIF-UH2C/acpa-msmda`, la branche `main`
   et le fichier principal `app.py`.
5. Dans **Advanced settings**, choisir **Python 3.12** (même version que la CI).
   Pour une application déjà déployée, vérifier la version utilisée dans ses
   réglages ; la changer peut demander de supprimer puis redéployer l'application.
6. Choisir une adresse d'application et cliquer sur **Deploy**.
7. Tester dans le navigateur de l'ordinateur et du téléphone avec des
   contextes **entièrement fictifs**.

Ne jamais sélectionner le dépôt privé `acpa-msmda-dev` pour cette publication :
son serveur HTTP et son récepteur de synchronisation sont conçus uniquement
pour la machine locale, sans mécanisme d'authentification distant.

## Contraintes et points de vigilance

- Le dépôt et cette démonstration sont publics ; aucune donnée sensible ne doit
  être saisie ni envoyée à l'hébergeur.
- L'application ne sauvegarde pas les requêtes dans une base de données, mais
  l'opérateur d'hébergement peut traiter des données techniques de session.
- Les suggestions de technologies reposent sur une correspondance de mots-clés
  avec les fiches documentées ; aucun score n'est attribué aux outils réels.
- L'application ne propose ni comptes utilisateurs, ni véritable catalogue
  d'outils évalués, ni droits d'accès, ni synchronisation serveur.
- Avant tout usage réel, prévoir catalogue autorisé et vérifié, validation
  scientifique, politique de confidentialité, gestion des accès, tests de
  sécurité et évaluation juridique de la diffusion.

Documentation officielle :
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
