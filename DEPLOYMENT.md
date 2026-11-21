# Déployer la démonstration web ACPA/MSMDA

Cette interface Streamlit est une **démonstration scientifique** du moteur heuristique
déjà publié. Elle utilise exclusivement les cinq profils fictifs contenus dans
data/synthetic_tools.json. Il ne s'agit pas de l'application ACPA/MSMDA complète,
ni d'une recommandation scientifiquement validée pour les enseignants.

## Lancement local

Pré-requis : Python 3.11 ou 3.12.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Le navigateur ouvre une interface trilingue (FR, EN, AR) dans laquelle on peut :
1. décrire un contexte EPS fictif ;
2. exécuter les règles de détection et de pondération du moteur public ;
3. consulter les cinq scores composites et relatifs ;
4. vérifier les 18 pondérations et exporter un résultat JSON.

## Mise en ligne avec Streamlit Community Cloud

1. Examiner cette branche et fusionner la pull request après validation.
2. Aller sur https://share.streamlit.io et se connecter avec GitHub.
3. Choisir **Create app → Yup, I have an app**.
4. Renseigner le dépôt `LMSEIF-UH2C/acpa-msmda`, la branche `main`
   et le fichier principal `app.py`.
5. Choisir une adresse d'application et cliquer sur **Deploy**.
6. Tester dans le navigateur de l'ordinateur et du téléphone avec des
   contextes **entièrement fictifs** en français, anglais et arabe.

Ne jamais sélectionner le dépôt privé `acpa-msmda-dev` pour cette publication :
son serveur HTTP et son récepteur de synchronisation sont conçus uniquement
pour la machine locale, sans mécanisme d'authentification distant.

## Contraintes et points de vigilance

- Le dépôt et cette démonstration sont publics ; aucune donnée sensible ne doit
  être saisie ni envoyée à l'hébergeur.
- L'application ne sauvegarde pas les requêtes dans une base de données, mais
  l'opérateur d'hébergement peut traiter des données techniques de session.
- Les scores du catalogue sont fictifs, le modèle est à règles et la valeur
  relative de 100 n'est **pas** une preuve de qualité parfaite.
- L'application ne propose ni comptes utilisateurs, ni véritable catalogue
  d'outils évalués, ni droits d'accès, ni synchronisation serveur.
- Avant tout usage réel, prévoir catalogue autorisé et vérifié, validation
  scientifique, politique de confidentialité, gestion des accès, tests de
  sécurité et évaluation juridique de la diffusion.

Documentation officielle :
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
