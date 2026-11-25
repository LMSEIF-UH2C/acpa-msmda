# REC-Y002 — Barre de navigation sur iPhone réel

- Date : 25 novembre 2026.
- Source : capture réelle fournie par le porteur (page d'accueil, iPhone, FR, Streamlit Cloud administrateur).
- Observations : barre démarrant au milieu de l'écran, onglets hors écran, recouvrement par « Manage app ». Le recouvrement de contenu à l'écran demande aussi un contrôle en fin de défilement.
- Hypothèse de cause : le sélecteur d'animation générique peut s'appliquer à la barre ou à un ancêtre ; la propriété transform animée entre en conflit avec translateX(-50%) ou crée un bloc contenant pour position:fixed. La capture seule ne prouve pas la cause exacte.

## Correction proposée
Centrage sans transform, par bords physiques et marges automatiques, largeur maximale préservée, prise en compte des safe areas, animation limitée à l'opacité, cinq colonnes compressibles et libellés pouvant revenir à la ligne. Aucun changement de navigation, de données, de moteur scientifique, de dépendances applicatives ou d'identité graphique. Pas de masquage supplémentaire des contrôles Streamlit Cloud.

## Validation
`scripts/check_mobile_navigation.py` vérifie la géométrie et les cibles de toucher de chaque onglet, en Chromium et WebKit, pour 320/375/390/414/430 px et FR/AR/EN, au chargement et après défilement. Workflow dédié : `.github/workflows/mobile-navigation.yml`.

**Statut au dépôt :** tests navigateur ajoutés mais pas encore exécutés par ChatGPT. Le test sur iPhone réel avec barres de navigateur, orientation et clavier, ainsi que le test visiteur / administrateur Streamlit Cloud, restent indispensables. Le contrôle « Manage app » peut appartenir à l'enveloppe d'hébergement et ne pas être contrôlable par le CSS de l'application. Ne pas masquer ce contrôle ni déclarer la correction validée avant la recette réelle.

La PR #68 (banque visuelle) reste indépendante.
