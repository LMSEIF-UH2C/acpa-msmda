# REC-Y001 — incident de recette iPhone, 24 novembre 2026

Le porteur du projet a importé le fichier synthétique longitudinal (2880 observations). Le tableau apparié était visible, puis TypeError: _TypedDictMeta.__new__() got an unexpected keyword argument 'closed'. Capture IMG_6310; environnement affiché Python 3.14. Les CI précédentes utilisaient Python 3.12, Altair 5.5.0 et Streamlit 1.47.1.

Correctif candidat : Altair 6.0.0 et Streamlit 1.52.0 (support annoncé Python 3.14 et Altair 6), matrice CI 3.12/3.14 avec pip check, isolation des trois graphiques du laboratoire et maintien des tableaux/exports en cas d'exception. Aucun changement des calculs statistiques. La cause exacte dans l'environnement public reste à confirmer par le retest.

Sources : https://github.com/vega/altair/issues/3908 ; https://docs.streamlit.io/develop/quick-reference/release-notes/2025

Critères de clôture : CI verte sur les deux versions, validation R, fusion contrôlée, confirmation de la révision déployée et reproduction du test sur iPhone. Statut : ouvert, correctif candidat.
