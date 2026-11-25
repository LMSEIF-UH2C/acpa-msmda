# Recette physique iPhone v0.2.0

À exécuter sur le déploiement final (révision à noter ci-dessous), après fusion des PR retenues. Un essai avec le micro réel n'est pas équivalent aux simulations de la CI : les cases ci-dessous restent à cocher par une personne, sur l'appareil.

Appareil : ............ iOS : ............ Safari : ............
Révision déployée (pied de page ou journal Streamlit) : ............ Date : ............

Utiliser uniquement des données fictives : aucun nom d'élève, code Massar ni date de naissance.

## 1. Navigation et affichage

- [ ] Accueil en FR, AR, EN : barre d'onglets centrée, sans débordement latéral, contour blanc et vert continu autour du bandeau.
- [ ] Défilement jusqu'à la dernière carte de chaque page ; aucun élément masqué par la barre d'onglets.
- [ ] Arabe : alignement à droite, chiffres et unités lisibles, police arabe chargée.
- [ ] Rotation portrait/paysage sans perte de saisie.
- [ ] Badge Streamlit Community Cloud : noter s'il recouvre la barre d'onglets (limite connue N5, hors code de l'application).

## 2. Dictée vocale (micro réel)

- [ ] Autoriser le micro dans Safari ; le refus affiche un message compréhensible.
- [ ] Dictée en arabe : texte affiché sur plusieurs lignes, de droite à gauche, sans coupure.
- [ ] Après « Arrêter », le texte est transféré une seule fois dans le champ de recherche (pas de doublon).
- [ ] Fin automatique après silence : si Safari émet la fin de reconnaissance, le texte reconnu est transféré une seule fois. Sinon, toucher « Arrêter » ; si Safari n'émet pas de fin, le mécanisme de secours transfère le dernier texte reconnu après environ 1,8 s.
- [ ] Dictée en français, puis phrase bilingue arabe et français : transfert complet.
- [ ] La recherche lancée avec le texte dicté renvoie des résultats cohérents.

## 3. Sauvegardes Excel

- [ ] Évaluation formative : remplir une classe fictive, « Sauvegarder mes évaluations (Excel) », ouvrir le fichier dans Fichiers ou Numbers.
- [ ] Recharger la page, restaurer ce fichier : données identiques.
- [ ] Cahier journalier : sauvegarde puis restauration d'un journal contenant au moins une séance et un projet de classe.
- [ ] Projets de cycle : sauvegarde puis restauration.
- [ ] Un fichier modifié avec une formule est refusé avec un message clair.

## 4. PDF

- [ ] Export PDF en arabe : lettres liées, sens de lecture correct, aucun carré vide.
- [ ] Export PDF en français et en anglais.

## 5. Laboratoire

- [ ] Test avec illustration (par exemple Ruffier, Sargent, sprint 30 m) : ouvrir « Illustration pédagogique », image chargée, légende dans la langue active, mention « Illustration générée par IA, non normative » visible.
- [ ] Test avec pictogramme (par exemple handgrip) : pictogramme affiché avec la mention « Pictogramme de famille, pas une illustration du protocole ».
- [ ] Souplesse assise : constater que l'élève est chaussé (réserve documentée).
- [ ] Restitution à trois niveaux : « Comprendre », « Analyser » et « Investiguer » accessibles et lisibles sur l'écran étroit.
- [ ] Crédits et licences visibles dans « Statut scientifique et sources ».

## Résultat

| Section | Conforme | Anomalie (description, capture) |
|---|---|---|
| 1. Navigation | | |
| 2. Dictée | | |
| 3. Excel | | |
| 4. PDF | | |
| 5. Laboratoire | | |

Une anomalie bloquante est une perte ou une altération de données, un export illisible, un parcours impossible à terminer ou un texte dicté perdu. Le reste est consigné comme limite non bloquante.
