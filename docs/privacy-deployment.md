# Confidentialité et déploiement

## Données et limites

- Ne saisir aucun nom, identifiant d'élève ou donnée personnelle sensible. Utiliser des codes de groupes non nominatifs et des exemples fictifs pendant les essais.
- Le contexte, le scénario, les mesures et le journal utilisent la session Streamlit sur le serveur. La fermeture, l'expiration ou le redémarrage peuvent les effacer. Le journal possède une sauvegarde locale téléchargeable ; elle ne couvre pas tous les modules. Conserver les fichiers dans un espace approprié.
- Les photos pédagogiques sont transmises au serveur pour la session. Ne joindre aucune personne identifiable ; vérifier les droits.
- La dictée est facultative. Le navigateur peut utiliser son propre service distant de reconnaissance vocale. L'application reçoit le texte reconnu ; ne pas dicter de données d'élèves.
- Les avis enregistrent la fiche, le choix, la date et une variation de compteur dans un fichier serveur. Leur persistance dépend de l'hébergement. L'absence d'identifiant dans ce fichier ne garantit pas un anonymat absolu au niveau de l'hébergeur.
- Les liens vers les éditeurs ouvrent des services externes soumis à leurs propres conditions. Vérifier les permissions, l'âge requis, le coût et les règles institutionnelles.
- Les compagnons hors ligne et vidéo sont expérimentaux et séparés du service public.

## Déploiement

Lancer avec Python 3.12 et les dépendances du dépôt : `streamlit run app.py`. Vérifier les deux workflows GitHub, puis tester la démonstration publique dans un navigateur visiteur. En cas d'erreur de démarrage, consulter les logs dans le tableau de bord Streamlit, vérifier le dépôt, la branche et les dépendances, puis redémarrer si nécessaire. Sauvegarder le travail avant tout redémarrage. Ne pas masquer une exception persistante.

La recette réelle doit couvrir les trois langues, les petits écrans, les exports et la restauration. Un succès CI ne garantit ni conformité réglementaire ni accessibilité complète. L'utilisation institutionnelle nécessite une revue des conditions d'hébergement et des traitements.

Références :
- https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
- https://www.w3.org/TR/WCAG22/
